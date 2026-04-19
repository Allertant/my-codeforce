import sys
input = sys.stdin.readline

def solve():
    s = input()
    for ch in s:
        if ch == 'H' or ch == 'Q' or ch == '9':
            print("YES")
            return
    print("NO")
        

if __name__ == "__main__":
    solve() 