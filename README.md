# Capstone Project 135 JetBot
### control_pkg
    MPC Control algorithm
    Takes state of the JetBot and the path
    Outputs angular velocities on the two wheels
### path_pkg
    Generate desired path for the JetBot
    Takes obstacle map, start position, end position
    Outputs sequence of coordinates of the optimal path
#### path finder
    Correspond to the pathfinding algorithm section in the report, include test code for different algorithms
### vision_pkg
#### state (sub pkg)
        Video frame calibration, get JetBot state, get desired position
        Takes detected ArUco tag information and board_size
        
        state_estimation.py:
            get_state(calibrated corners and ids, board_size) (returns state of JetBot as np array [x, y, theta])
            get_desired_pos(calibrated corners and ids, board_size) (returns target position as np array [x, y])
        initialize.py:
            calib_frame(original frame, normal corners and ids, board_size) (returns calibrated img and homograph matrix)
#### detect_object (sub pkg)
        Generate obstacle map for A*
        Takes calibrated frame
        Outputs 2D np array of 0s and 1s, 0 being occupied space, 1 bing free space
        
        Camera.py:
            generate_map(calibrated frame) (returns the obstacle map)
