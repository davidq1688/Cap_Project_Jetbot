import heapq
# import time
# import pickle
import numpy as np

def A_star_algorithm(matrix, sx, xy, ex, ey):
    start = (sx, xy)
    end = (ex, ey)
    moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    cost = {}
    parent = {}
    pq = []
    cost[start] = 0
    num_nodes = 0
    
    heapq.heappush(pq, (0, start))
    
    while pq:
        curr_cost, curr_pos = heapq.heappop(pq)
        num_nodes += 1
        # debug
        print("calculating A*")
        if curr_pos == end:
            path = []
            while curr_pos in parent:
                path.append(curr_pos)
                curr_pos = parent[curr_pos]
            path.append(start)
            path.reverse()
            return np.asarray(path)
        
        for move in moves:
            neighbor_pos = (curr_pos[0] + move[0], curr_pos[1] + move[1])
            
            if not (0 <= neighbor_pos[0] < len(matrix) and 0 <= neighbor_pos[1] < len(matrix[0])):
                continue
            
            if matrix[neighbor_pos[0]][neighbor_pos[1]] == 1:
                continue
            
            new_cost = cost[curr_pos] + 1
            
            if neighbor_pos not in cost or new_cost < cost[neighbor_pos]:
                cost[neighbor_pos] = new_cost
                priority = new_cost + heuristic(neighbor_pos, end)
                heapq.heappush(pq, (priority, neighbor_pos))
                parent[neighbor_pos] = curr_pos
    
    print("No path found for A star")
    return None

def heuristic(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


# with open("grid.pkl", "rb") as f:
#     matrix = pickle.load(f)

# start = (10, 10)
# end = (90, 90)

# matrix[start[0]][start[1]] = 0
# matrix[end[0]][end[1]] = 0

# start_time = time.perf_counter()

# path = astar(matrix, start, end)

# elapsed_time = time.perf_counter() - start_time
# # print(path) 
# print("elapsed_time: ", elapsed_time)
