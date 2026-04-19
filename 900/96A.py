import sys
input = sys.stdin.readline

def solve():
    pos = input()
    ls = pos[0]
    lens = 1
    for ch in pos[1:]:
        if ch == ls:
            lens += 1
            if lens >= 7:
                print("YES")
                return 
        else:
            lens = 1
        ls = ch
    print("NO")

if __name__ == "__main__":
    solve() 
    