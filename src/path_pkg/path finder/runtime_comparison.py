# compare the runtime of the different algorithms with the maze size from 10*10 to 100*100
# iterately generate a maze with the same size
# and calculate the average runtime of 10 times and plot the result
# the result is saved in the file runtime_comparison.png in the same directory

import time
# import pickle
import random
import matplotlib.pyplot as plt

from maze_generator import generate_maze
from A_star import astar
from bfs import bfs
from dijkstra import dijkstra
from bellman_ford import bellman_ford

A_star_time = []
bfs_time = []
dijkstra_time = []
i = 200
iterations = 100
# iteratively generate maze size from 10*10 to i*i
# and calculate the average runtime of iterations times
# do bellman_ford separately as it takes too long
# record teh number of nodes expanded for A star
A_star_expanded_nodes = []
for i in range(10, i, 5):
    start = (0, 0)
    end = (i - 1, i - 1)
    A_star_time.append(0)
    bfs_time.append(0)
    dijkstra_time.append(0)
    A_star_expanded_nodes.append(0)
    print("maze size: ", i, " * ", i)
    for _ in range(iterations):
        grid = generate_maze(i)
        start_time = time.time()
        path, nodes = astar(grid, start, end)
        A_star_time[-1] += time.time() - start_time
        A_star_expanded_nodes[-1] += nodes
        start_time = time.time()
        bfs(grid, start, end)
        bfs_time[-1] += time.time() - start_time
        start_time = time.time()
        dijkstra(grid, start, end)
        dijkstra_time[-1] += time.time() - start_time
        start_time = time.time()
        # bellman_ford(grid, start, end)
        # bellman_ford_time[-1] += time.time() - start_time
    A_star_time[-1] /= iterations
    bfs_time[-1] /= iterations
    dijkstra_time[-1] /= iterations
    A_star_expanded_nodes[-1] /= iterations
    # bellman_ford_time[-1] /= iterations

# plot the result
plt.plot(range(10, i + 1, 5), A_star_time, label='A_star')
plt.plot(range(10, i + 1, 5), bfs_time, label='bfs')
plt.plot(range(10, i + 1, 5), dijkstra_time, label='dijkstra')
# plt.plot(range(10, i, 5), bellman_ford_time, label='bellman_ford')

plt.xlabel('maze size')
plt.ylabel('runtime')
plt.legend()
plt.title('runtime comparison')
plt.savefig('runtime_comparison.png')

# plot A star solely
plt.clf()
plt.plot(range(10, i + 1, 5), A_star_time, label='A_star')
plt.xlabel('maze size')
plt.ylabel('runtime')
plt.legend()
plt.title('A star runtime')
plt.savefig('A_star_runtime_comparison.png')

# plot A star expanded nodes vs maze size
plt.clf()
plt.plot(range(10, i + 1, 5), A_star_expanded_nodes, label='A_star')
plt.plot(range(10, i + 1, 5), [i * i for i in range(10, i + 1, 5)], label='maze size')
plt.xlabel('maze size')
plt.ylabel('expanded nodes')
plt.legend()
plt.title('A star expanded nodes')
plt.savefig('A_star_expanded_nodes_comparison.png')

# test bellman_ford for 10*10 to 40*40
bellman_ford_time = []
for i in range(10, 41, 5):
    start = (0, 0)
    end = (i - 1, i - 1)
    bellman_ford_time.append(0)
    print("maze size: ", i, " * ", i)
    for _ in range(3):
        grid = generate_maze(i)
        start_time = time.time()
        bellman_ford(grid, start, end)
        bellman_ford_time[-1] += time.time() - start_time
    bellman_ford_time[-1] /= 3

# plot bellman_ford result
plt.clf()
plt.plot(range(10, 41, 5), bellman_ford_time, label='bellman_ford')
plt.xlabel('maze size')
plt.ylabel('runtime')
plt.legend()
plt.title('bellman_ford runtime')
plt.savefig('bellman_ford_runtime_comparison.png')