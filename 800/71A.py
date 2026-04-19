import sys
input = sys.stdin.readline

def solve():
    n = int(input().strip())
    words = []
    for i in range(n):
        word = input().strip()
        if len(word) > 10:
            words.append(word[0:1] + str(len(word) - 2) + word[-1])
        else:
            words.append(word)
    
    # print
    for word in words:
        print(word)
        

if __name__ == "__main__":
    solve()