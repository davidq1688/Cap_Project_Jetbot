import numpy as np
import cv2
import time
import socket, json
import matplotlib.pyplot as plt

from vision_pkg.state.initialize import calib_frame
from vision_pkg.state import state_estimation
from vision_pkg.state.state_estimation import get_state
from vision_pkg.detect_object.Camera import generate_map
from control_pkg.heading_angle_generator import heading_angle_generator
from control_pkg.cftoc import solve_cftoc
from path_pkg.main import A_star_algorithm

# port & UDP
UDP_IP = "172.20.10.11"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Measure the board size [length, height] in mm
# length is the distance from top left to top right (tag 0 to tag 3)
# height is the distance from top left to bottom left (tag 0 to tag 1)
board_size = [1080, 860]
A_star_board_size = [int(board_size[0]/10), int(board_size[1]/10)]

# speed to PWM ratio (PWM/speed)
ratio = 1/0.94

cap = cv2.VideoCapture(0)
arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
arucoParams = cv2.aruco.DetectorParameters_create()

# Initialize (find obstacle map, find path)
# 1st while: generate obstacle map
while True:
    ret, img = cap.read()
    (corners, ids, rejected) = cv2.aruco.detectMarkers(img, arucoDict,
                                                       parameters=arucoParams)
    cv2.imshow("not calibrated", img)
    key = cv2.waitKey(2000) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
    if len(corners) > 3:
        ids = ids.flatten()
        if 0 in ids and 1 in ids and 2 in ids and 3 in ids:
            calibrated_img, homograph_matrix = calib_frame(img, corners, ids, board_size)
            A_star_calib_img, A_star_H = calib_frame(img, corners, ids, A_star_board_size)
            # cv2.imshow("calibrated", calibrated_img)
            # cv2.waitKey(1000)
            break
cv2.destroyAllWindows()
print('obtained calibrated img')
# NOTE: row correspond to y, col correspond to x
A_star_map, dilated_mask = generate_map(A_star_calib_img)
dilated_mask_resized = cv2.resize(dilated_mask, board_size)

# Create transparent overlay for debugging
alpha = 0.5
overlay = np.zeros(dilated_mask_resized.shape, dtype='uint8')
overlay = cv2.addWeighted(overlay, 1-alpha, dilated_mask_resized, alpha, 0)
overlay = cv2.bitwise_and(overlay, dilated_mask_resized)

# print(A_star_map)

# 2nd while: find start and end position:
while True:
    ret, img = cap.read()
    (corners, ids, rejected) = cv2.aruco.detectMarkers(img, arucoDict,
                                                       parameters=arucoParams)

    if len(corners) >= 2:
        ids = ids.flatten()
        can_see_corners = 0 in ids and 1 in ids and 2 in ids and 3 in ids
        if can_see_corners and 4 in ids and 5 in ids:
            start_state = state_estimation.get_state_old(corners, ids, A_star_board_size)
            start_pos = start_state[0:2]
            end_pos = state_estimation.get_desired_pos_old(corners, ids, A_star_board_size)
            break

print('start and end position found')
# Now have A_star_map, start_pos, end_pos
# start_pos and end_pos are lists of int [x, y]

# convert start_pos and end_pos from [x,y] to [row, col] to feed to A* algorithm
start_coord = np.array([start_pos[1], start_pos[0]], dtype=np.uint8)
end_coord = np.array([end_pos[1], end_pos[0]])
# print('A_star_size: ', A_star_map.shape)
# print('start_coord ', start_coord)
# print('end_coord ', end_coord)

# feed A_star_map and start_pos, end_pos to generate path
# f = open("tmp_debugger.txt", "w")
# f.write(str(A_star_map))
# f.close()
# np.savetxt('tmp_Astar', A_star_map, fmt='%d')
path = A_star_algorithm(A_star_map, start_coord[0], start_coord[1], end_coord[0], end_coord[1])
if path is None:
    print('No path found')
    exit()
print('Found optimal path')

# Run MPC
current_state = np.array([start_state[0]*10, start_state[1]*10, start_state[2]])
print(type(path))
optimal_path = heading_angle_generator(path, current_state[2])

M = 0

max_iteration = (np.size(optimal_path[:, 0]) - 1)
terminal_x = optimal_path[-1, 0]
terminal_y = optimal_path[-1, 1]

ul_prev = 2
ur_prev = 2

jetbot_x_tot = []
jetbot_y_tot = []
jetbot_th_tot = []
x_des_tot = []
y_des_tot = []
th_des_tot = []

while True:
    tic = time.time()
    ret, img = cap.read()

    calibrated_frame = cv2.warpPerspective(img, homograph_matrix, np.array(board_size))
    # resized_frame = cv2.resize(calibrated_frame, (500, int(500/board_size[1]*board_size[0])))
    result_frame = cv2.add(calibrated_frame, overlay)

    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        MESSAGE = json.dumps({"left": 0, "right": 0})
        sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
        break

    (calib_corners, calib_ids, calib_rej) = cv2.aruco.detectMarkers(calibrated_frame, arucoDict,
                                                                    parameters=arucoParams)
    if len(calib_corners) > 0:
        calib_ids.flatten()
        if 4 in calib_ids:
            current_state = get_state(calib_corners, calib_ids, board_size)
            # print(current_state)

    # save jetbot states in m and rad
    jetbot_x_tot.append(current_state[0]*0.001)
    jetbot_y_tot.append(current_state[1]*0.001)
    jetbot_th_tot.append(current_state[2])

    # save desired state for each loop
    x_des_tot.append(optimal_path[M+1, 0])
    y_des_tot.append(optimal_path[M+1, 1])
    th_des_tot.append(optimal_path[M+1, 2])

    # current position are in meters and rads whereas current_state are in mm and rads
    current_position = np.array([current_state[0]*0.001, current_state[1]*0.001, current_state[2]])

    # norm between current point and desired point. Used to determine if we can move to the next point
    distance_throttle = (current_position[0] - optimal_path[M+1, 0])**2 + (current_position[1] - optimal_path[M+1, 1])**2

    # Calling MPC
    [omega_L_opt, omega_R_opt] = solve_cftoc(current_position, optimal_path[M+1, :], ul_prev, ur_prev)
    ul_prev = omega_L_opt
    ur_prev = omega_R_opt

    # Debugging test
    for i in range(max_iteration):
        cv2.circle(result_frame,
                   (int(optimal_path[i, 0] * 1000), int(board_size[1] - optimal_path[i, 1] * 1000)), 4,
                   (0, 255, 255), -1)

    cv2.circle(result_frame, (int(optimal_path[M+1, 0]*1000), int(board_size[1] - optimal_path[M+1, 1]*1000)), 4, (0, 0, 255), -1)
    # cv2.imshow("debugging window", result_frame)
    resized_result = cv2.resize(result_frame, (500, int(500 / board_size[0] * board_size[1])))
    cv2.imshow('resized debugging window', resized_result)

    # print('Max Iteration: ', max_iteration)
    # print('M: ', M)
    # print('distance: ', np.sqrt(distance_throttle))
    if M < max_iteration - 1:
        # threshold distance (in m)
        if distance_throttle < 0.06**2:
            M += 1
    else:
        if distance_throttle < 0.04**2:
            # print('distance', np.sqrt(distance_throttle))
            M += 1

    # Terminate when it reaches the final point
    if M == max_iteration:
        MESSAGE = json.dumps({"left": 0, "right": 0})
        sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
        print('Reached Max Iteration')
        break

    # print('current position: ', current_position)
    # print('desired next point: ', optimal_path[M+1, :])

    # print(omega_R_opt, omega_L_opt)
    right = int(omega_R_opt*100)
    left = int(omega_L_opt*100)

    MESSAGE = json.dumps({"right": right, "left": left})
    sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
    time.sleep(0.05)

    toc = time.time()
    time_loop = toc - tic
    # print('time_loop: ', time_loop)

plt.figure(1)
plt.plot(x_des_tot, y_des_tot, 'ro', label='Desired path')
plt.plot(jetbot_x_tot, jetbot_y_tot, label='Actual path')
plt.legend()
plt.xlabel('x (m)')
plt.ylabel('y (m)')

plt.figure(2)
plt.plot(th_des_tot, label='Desired angle')
plt.plot(jetbot_th_tot, label='Actual angle')
plt.legend()
plt.xlabel('Discrete time step')
plt.ylabel('Angle (rad)')

plt.show()
