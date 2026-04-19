import sys
input = sys.stdin.readline

def solve():
    n, m, a = list(map(int, input().split()))
    l1 = n // a if n % a == 0 else n // a + 1
    l2 = m // a if m % a == 0 else m // a + 1
    print(l1 * l2)

if __name__ == "__main__":
    solve() 