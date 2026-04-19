import sys
input = sys.stdin.readline

def solve():
    s = input().strip()
    ans= ''
    for ch in s:
        if ch in ['A', 'O', 'Y', 'E', 'U', 'I', 'a', 'o', 'y', 'e', 'u', 'i']:
            continue
        if ord(ch) >= 65 and ord(ch) <= 90:
            ch = chr(ord(ch) + 32)
            
        ans += '.' + ch
    print(ans)

if __name__ == "__main__":
    solve() 