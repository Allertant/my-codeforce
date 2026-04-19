import sys
input = sys.stdin.readline

def solve():
    n, k = list(map(int, input().split()))
    pars = list(map(int, input().split()))
    
    # 边界条件
    if k > n:
        print(0)
        return
    
    target = pars[k - 1]
    
    # 由于要判定整数, 因此这里需要完整遍历
    ans = 0
    for par in pars:
        if par >= target and par > 0:
            ans += 1
            
    print(ans)
    

if __name__ == "__main__":
    solve() 