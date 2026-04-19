import sys
input = sys.stdin.readline

def solve():
    n = int(input())
    cntx = cnty = cntz = 0
    for i in range(n):
        x, y, z = list(map(int, input().split()))
        cntx += x
        cnty += y
        cntz += z
    if cntx == 0 and cnty == 0 and cntz == 0:
        print('YES')
    else:
        print("NO")

if __name__ == "__main__":
    solve() 