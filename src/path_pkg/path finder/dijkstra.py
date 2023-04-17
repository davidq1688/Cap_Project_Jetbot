import heapq
# import time

def dijkstra(matrix, start, end):
    moves = [(0, 1), (0, -1), (1, 0), (-1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    rows = len(matrix)
    cols = len(matrix[0])
    distance = [[float('inf') for j in range(cols)] for i in range(rows)]
    visited = [[False for j in range(cols)] for i in range(rows)]
    distance[start[0]][start[1]] = 0
    prev = [[None for j in range(cols)] for i in range(rows)]
    heap = [(0, start)]

    while heap:
        curr_dist, curr_pos = heapq.heappop(heap)

        if curr_pos == end:
            path = []
            while curr_pos is not None:
                path.append(curr_pos)
                curr_pos = prev[curr_pos[0]][curr_pos[1]]
            return path[::-1]

        if visited[curr_pos[0]][curr_pos[1]]:
            continue

        visited[curr_pos[0]][curr_pos[1]] = True

        for move in moves:
            neighbor = (curr_pos[0] + move[0], curr_pos[1] + move[1])

            if not (0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and matrix[neighbor[0]][neighbor[1]] == 0):
                continue
            
            dist = curr_dist + 1 if move[0] == 0 or move[1] == 0 else curr_dist + 1.4

            if dist < distance[neighbor[0]][neighbor[1]]:
                distance[neighbor[0]][neighbor[1]] = dist
                prev[neighbor[0]][neighbor[1]] = curr_pos
                heapq.heappush(heap, (dist, neighbor))

    return None

# with open("grid.pkl", "rb") as f:
#     matrix = pickle.load(f)

# start = (10, 10)
# end = (90, 90)

# matrix[start[0]][start[1]] = 0
# matrix[end[0]][end[1]] = 0

# start_time = time.perf_counter()

# path = dijkstra(matrix, start, end)
# # print(path)
# elapsed_time = time.perf_counter() - start_time

# print("elapsed_time: ", elapsed_time)
