import sys
input = sys.stdin.readline

def solve():
    n = int(input())
    cnt = 0
    for i in range(n):
        li = list(map(int, input().split()))
        if sum(li) >= 2:
            cnt += 1
    print(cnt)

if __name__ == "__main__":
    solve()