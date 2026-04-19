import sys
input = sys.stdin.readline

def solve():
    s = input().strip()
    lens = len(set(s))
    ans = 'CHAT WITH HER!' if lens % 2 == 0 else "IGNORE HIM!"
    print(ans)

if __name__ == "__main__":
    solve()