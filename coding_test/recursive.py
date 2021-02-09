"""
1부터 100까지 합
1. x = 0
2. x += 1
3. x += 2
4. x += 3
5. x += 4
6. ...
7. x += 100
"""

x = 0
for i in range(1,101):
    x += i

print(x)


"""
1부터 100까지 합
1. x = 0
2. x *= 1
3. x *= 2
4. x *= 3
5. x *= 4
6. ...
7. x *= 100
"""

# 팩토리얼
x = 1
for i in range(1,6):
    x *= i

print(x)


# 재귀함수
def f(n):
    if n <= 1:
        return 1
    else:
        return n + f(n-1)

n = 100
print(f(n))
