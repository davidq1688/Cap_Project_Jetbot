# import time

def bellman_ford(matrix, start, end):
    moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    dist = {(i, j): float('inf') for j in range(len(matrix[0])) for i in range(len(matrix))}
    pred = {(i, j): None for j in range(len(matrix[0])) for i in range(len(matrix))}
    dist[start] = 0
    
    for _ in range(len(matrix) * len(matrix[0]) - 1):
        for x, y in dist:
            if matrix[x][y] == 1:
                continue
            for move in moves:
                nx, ny = x + move[0], y + move[1]
                if 0 <= nx < len(matrix) and 0 <= ny < len(matrix[0]) and matrix[nx][ny] == 0:
                    w = 1
                    if (nx, ny) == end:
                        w = 0
                    if dist[(nx, ny)] > dist[(x, y)] + w:
                        dist[(nx, ny)] = dist[(x, y)] + w
                        pred[(nx, ny)] = (x, y)
    
    path = []
    node = end
    while node:
        path.append(node)
        node = pred[node]
    path.reverse()
    
    return path, dist[end]

# matrix = [[0, 0, 1, 0, 0],
#           [0, 0, 0, 0, 1],
#           [0, 1, 0, 0, 0],
#           [0, 0, 0, 0, 0],
#           [1, 0, 1, 0, 0]]

# start = (0, 0)
# end = (4, 4)

# Too heavy fot this algorithm, do not use ~ 90 seconds runtime
# with open("grid.pkl", "rb") as f:
#     matrix = pickle.load(f)

# start = (10, 10)
# end = (90, 90)

# matrix[start[0]][start[1]] = 0
# matrix[end[0]][end[1]] = 0

# start_time = time.perf_counter()
# path, distance = bellman_ford(matrix, start, end)
# elapsed_time = time.perf_counter() - start_time

# # print(path)
# print("Elapsed time:", elapsed_time)
