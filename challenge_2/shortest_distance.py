from collections import deque

def shortest_distance_to_house(grid):
    if not grid:
        return grid

    n, m = len(grid), len(grid[0])
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    distances = [[float('inf')] * m for _ in range(n)]
    visited = [[False] * m for _ in range(n)]
    queue = deque()

    # Find all houses and mark them as visited
    for i in range(n):
        for j in range(m):
            if grid[i][j] == 'H':
                queue.append((i, j, 0))
                visited[i][j] = True

    # Perform multi-source BFS from all houses simultaneously
    while queue:
        i, j, d = queue.popleft()
        distances[i][j] = d
        for dx, dy in directions:
            ni, nj = i + dx, j + dy
            if 0 <= ni < n and 0 <= nj < m and not visited[ni][nj]:
                visited[ni][nj] = True
                queue.append((ni, nj, d + 1))

    return distances

# Example usage:
grid = [
    [0, 0, 0],
    [0, 'N', 0],
    ['H', 'N', 'H']
]
result = shortest_distance_to_house(grid)
for row in result:
    print(*row)
