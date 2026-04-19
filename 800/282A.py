import sys
input = sys.stdin.readline

def solve():
    n = int(input())
    x = 0
    for i in range(n):
        oper = input()
        if "++" in oper:
            x += 1
        else:
            x -= 1
    print(x)

if __name__ == "__main__":
    solve()