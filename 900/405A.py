import sys
input = sys.stdin.readline

def solve():
    n = int(input())
    cols = list(map(int, input().split()))
    m = max(cols)
    matrix = [[0] * n for _ in range(m)]
    for j, col in enumerate(cols):
        for i in range(m - 1, m - col - 1, -1):
            matrix[i][j] = 1
    for row in matrix:
        sm = sum(row)
        row[(n - sm):] = [1] * (sm)
        row[0:(n - sm)] = [0] * (n - sm)
    ans = [sum(col) for col in zip(*matrix)]
    for x in ans:
        print(x, end=' ')
    print()

if __name__ == "__main__":
    solve() 