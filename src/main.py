import numpy as np
import cv2
import time
import socket, json

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
board_size = [100, 100]

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
    key = cv2.waitKey(1000) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
    if len(corners) > 3:
        ids = ids.flatten()
        if 0 in ids and 1 in ids and 2 in ids and 3 in ids:
            calibrated_img, homograph_matrix = calib_frame(img, corners, ids, board_size)
            # cv2.imshow("calibrated", calibrated_img)
            # cv2.waitKey(1000)
            break
cv2.destroyAllWindows()
print('obtained calibrated img')
# NOTE: row correspond to y, col correspond to x
A_star_map = generate_map(calibrated_img)

# 2nd while: find start and end position:
while True:
    ret, img = cap.read()
    (corners, ids, rejected) = cv2.aruco.detectMarkers(img, arucoDict,
                                                       parameters=arucoParams)

    if len(corners) >= 2:
        ids = ids.flatten()
        can_see_corners = 0 in ids and 1 in ids and 2 in ids and 3 in ids
        if can_see_corners and 4 in ids and 5 in ids:
            start_state = state_estimation.get_state_old(corners, ids, board_size)
            start_pos = start_state[0:2]
            end_pos = state_estimation.get_desired_pos_old(corners, ids, board_size)
            break

print('start and end position found')
# Now have A_star_map, start_pos, end_pos
# start_pos and end_pos are lists of int [x, y]

# convert start_pos and end_pos from [x,y] to [row, col] to feed to A* algorithm
start_coord = np.array([start_pos[1], start_pos[0]], dtype=np.uint8)
end_coord = np.array([end_pos[1], end_pos[0]])
# TODO: feed A_star_map and start_pos, end_pos to generate path
# MESSAGE = json.dumps({"msg": "Feeding matrix to A star"})
# sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
# print('start_coord[0]', start_coord[0])
path = A_star_algorithm(A_star_map, start_coord[0], start_coord[1], end_coord[0], end_coord[1])
print('Found optimal path')

# Run MPC
current_state = start_state

optimal_path = heading_angle_generator(path, current_state[2])

M = 0
max_iteration = np.size(optimal_path[:, 0]) - 1
terminal_x = optimal_path[-1, 0]
terminal_y = optimal_path[-1, 1]

while True:
    # tic = time.time()
    ret, img = cap.read()

    calibrated_frame = cv2.warpPerspective(img, homograph_matrix, np.array(board_size))
    cv2.imshow("calibrated", cv2.resize(calibrated_frame, (500, int(500/board_size[1]*board_size[0]))))
    cv2.waitKey(1)

    (calib_corners, calib_ids, calib_rej) = cv2.aruco.detectMarkers(calibrated_frame, arucoDict,
                                                                    parameters=arucoParams)
    if len(calib_corners) > 0:
        calib_ids.flatten()
        if 4 in calib_ids:
            current_state = get_state(calib_corners, calib_ids, board_size)
            print(current_state)

    # TODO: call MPC

    current_position = np.array([current_state[0]*0.01, current_state[1]*0.01, current_state[2]])

    [omega_L_opt, omega_R_opt] = solve_cftoc(current_position, optimal_path[M+1, :])

    print(omega_R_opt, omega_L_opt)
    right = int(omega_R_opt*100)
    left = int(omega_L_opt*100)

    MESSAGE = json.dumps({"right": right, "left": left})
    sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
    M += 1

    if M == max_iteration:
        MESSAGE = json.dumps({"left": 0, "right": 0})
        sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
        break

    terminal_norm = (current_state[0]*0.01 - terminal_x)**2 + (current_state[1]*0.01 - terminal_y)**2

    if terminal_norm < 0.0016:
        MESSAGE = json.dumps({"left": 0, "right": 0})
        sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
        break

    # toc = time.time()
    # time_loop = toc - tic

