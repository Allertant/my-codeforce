import sys
input = sys.stdin.readline

def solve():
    n = int(input())
    ans = 'YES' if n % 2 == 0 and n > 2 else 'NO'
    print(ans)

if __name__ == "__main__":
    solve()