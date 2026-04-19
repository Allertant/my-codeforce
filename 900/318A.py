import sys
input = sys.stdin.readline

def solve():
    n, k = list(map(int, input().split()))
    odd_cnt = n // 2 if n % 2 == 0 else n // 2 + 1
    even_cnt = n - odd_cnt
    ans = 0
    if k <= odd_cnt:
        ans = 2 * k - 1
    else:
        ans = (k - odd_cnt) * 2
    print(ans)
if __name__ == "__main__":
    solve() 