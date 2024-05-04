def find_pillars(matrix):
    n = len(matrix)
    m = len(matrix[0])
    pillars = []

    row_max = [max(row) for row in matrix]
    col_max = [max(col) for col in zip(*matrix)]

    for i in range(n):
        for j in range(m):
            if matrix[i][j] == row_max[i] == col_max[j]:
                pillars.append((i, j))

    return pillars

matrix = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
]
print(find_pillars(matrix))
