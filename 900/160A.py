import sys
input = sys.stdin.readline

def solve():
    n = int(input().strip())
    coins = list(map(int, input().split()))
    coins = sorted(coins, reverse=True)
    cnt = 0
    total = sum(coins)
    cur_total = 0
    for coin in coins:
        cur_total += coin
        cnt += 1
        if cur_total > total - cur_total:
            break
    print(cnt)
    

if __name__ == "__main__":
    solve() 