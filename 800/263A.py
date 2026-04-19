import sys
import math
input = sys.stdin.readline

def solve():
    n = 5
    x, y = 0, 0
    for i in range(n):
        ls = list(map(int, input().split()))
        if 1 in ls:
            x = i
            y = ls.index(1)
    print(abs(2 - x) + abs(2 - y))

if __name__ == "__main__":
    solve() 