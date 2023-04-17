import random

def generate_maze(i):
    # Initialize the grid with walls
    grid = [[1 for _ in range(i)] for _ in range(i)]
    
    # Set the start and end positions
    start = (0, 0)
    end = (i-1, i-1)
    grid[start[0]][start[1]] = 0
    grid[end[0]][end[1]] = 0
    
    # Perform depth-first search to generate the maze
    stack = [start]
    visited = set([start])
    while stack:
        x, y = stack.pop()
        neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        random.shuffle(neighbors)
        for neighbor in neighbors:
            if neighbor[0] < 0 or neighbor[0] >= i or neighbor[1] < 0 or neighbor[1] >= i:
                continue
            if neighbor == end:
                visited.add(neighbor)
                grid[neighbor[0]][neighbor[1]] = 0
                return grid
            if neighbor in visited:
                continue
            visited.add(neighbor)
            grid[neighbor[0]][neighbor[1]] = 0
            stack.append(neighbor)
    
    return grid