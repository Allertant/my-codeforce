import sys
input = sys.stdin.readline

def solve():
    str1 = input()
    str2 = input()
    n = len(str1)
    ans = 0
    for i in range(n):
        a, b = str1[i].lower(), str2[i].lower()
        if a < b:
            ans = -1
            break
        elif a > b:
            ans = 1
            break
    print(ans)
    

if __name__ == "__main__":
    solve()