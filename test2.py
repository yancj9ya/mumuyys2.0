from random import randint


def fx(n, a, res):
    if n == 0:
        return randint(1, 10000)
    elif n == 8:
        b = 1 + 1 / fx(n - 1, a, res)
        # print(f"fx({n}) = {b}")
        res.append(b)
        return b
    else:
        b = randint(1, 10000) + 1 / fx(n - 1, a, res)
        # print(f"fx({n}) = {b}")
        res.append(b)
        return b


for i in range(1, 10):
    res = [1]
    fx(8, i, res)
    print([f"when a = {i}", res[1] < res[5], res[3] < res[8], res[6] < res[2], res[4] < res[7]])
