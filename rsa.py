import secrets


def main():
    simple_nums = sieve(30)

    p, q = get_random_simple_nums(simple_nums)
    n = p * q
    euler = (p - 1) * (q - 1)
    e = init_exponent(euler, simple_nums)

    print(f"p = {p} q = {q}")
    print(f"n = p * q = {p} * {q} ={n}")
    print(f"φ = (p - 1) * (q - 1) ={euler}")

    print(bezout_recursive(5, 7))

    d = reverse_element(e, euler, simple_nums)
    print(f"secret key: d ={d}")


def reverse_element(e, euler, simple_nums):
    d = [0]
    x = [0]
    y = [0]

    while d != 1:
        gcd_ext(e, euler, d, x, y)
        if d != 1:
            e = init_exponent(euler, simple_nums)

    print(f"open key: e ={e}")
    print(d, "=", x, "* e +", y, "* φ")

    result = (x[0] % euler + euler) % euler
    return result


def bezout_recursive(a, b):
    """A recursive implementation of extended Euclidean algorithm.
    Returns integer x, y and gcd(a, b) for Bezout equation:
    ax + by = gcd(a, b).
    """
    if not b:
        return 1, 0, a
    y, x, g = bezout_recursive(b, a % b)
    return x, y - (a // b) * x, g


def gcd_ext(a, b, d, x, y):
    if b == 0:
        d[0] = a
        x[0] = 1
        y[0] = 0
        return

    gcd_ext(b, a % b, d, x, y)

    s = y[0]
    y[0] = x[0] - int(a / b) * y[0]
    x[0] = s


def gcd(a, b):
    if b == 0:
        return a
    return gcd(b, a % b)


def sieve(limit):
    inter = []
    result = []

    for i in range(limit + 1):
        inter.append(i)
    inter[1] = 0

    i = 2
    while i * i < limit:
        if inter[i] != 0:
            j = i + i
            while j < limit + 1:
                inter[j] = 0
                j += i
        i += 1

    for i in range(limit + 1):
        if inter[i] != 0:
            result.append(inter[i])

    return result


def init_exponent(euler, simple_nums):
    e, _ = get_random_simple_nums(simple_nums)
    while e < euler and gcd(e, euler) != 1:
        e, _ = get_random_simple_nums(simple_nums)
    return e


def get_random_simple_nums(nums):
    return nums[secrets.randbelow(len(nums))], nums[secrets.randbelow(len(nums))]


if __name__ == "__main__":
    main()
