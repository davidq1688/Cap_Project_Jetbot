# import pickle
import time

def bfs(grid, start, end):
    moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    queue = [start]
    visited = set()
    parent = {start: None}
    visited.add(start)
    
    while queue:
        current = queue.pop(0)
        
        if current == end:
            path = [current]
            while current in parent:
                current = parent[current]
                path.append(current)
            return path[::-1]
        
        for move in moves:
            x, y = current[0] + move[0], current[1] + move[1]
            
            if 0 <= x < len(grid[0]) and 0 <= y < len(grid) and grid[y][x] == 0 and (x, y) not in visited:
                queue.append((x, y))
                visited.add((x, y))
                parent[(x, y)] = current
    print("No path found for BFS")
    return None

# with open("grid.pkl", "rb") as f:
#     matrix = pickle.load(f)

# start = (10, 10)
# end = (90, 90)

# matrix[start[0]][start[1]] = 0
# matrix[end[0]][end[1]] = 0

# start_time = time.perf_counter()

# path = bfs(matrix, start, end)

# elapsed_time = time.perf_counter() - start_time
# # print(path) 
# print("elapsed_time: ", elapsed_time)
