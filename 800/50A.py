import sys
input = sys.stdin.readline

def solve():
    m, n = list(map(int, input().split()))
    ans = m * n // 2
    print(ans)

if __name__ == "__main__":
    solve() 