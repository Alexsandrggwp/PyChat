import secrets
import time


def test_rsa():
    simple_nums = sieve(10000)

    p, q = get_random_simple_nums(simple_nums)
    n = p * q
    euler = (p - 1) * (q - 1)
    e = init_exponent(euler, simple_nums)

    print(f"p = {p} q = {q}")
    print(f"n = p * q = {p} * {q} = {n}")
    print(f"φ = (p - 1) * (q - 1) = {euler}")

    d = reverse_element(e, euler, simple_nums)
    print(f"secret key: d = {d}")

    message = 7777

    start_time = time.time()

    enc = pow(message, e, n)
    print(f"encripted: {enc}")

    dec = pow(enc, d, n)
    print(f"decripted: {dec}")

    print(f"{(time.time() - start_time)}")


def reverse_element(e, euler, simple_nums):
    d = 0

    while d != 1:
        x, y, d = gcd_ext(e, euler)
        if d != 1:
            e = init_exponent(euler, simple_nums)

    print(f"open key: e = {e}")
    print(d, "=", x, "* e +", y, "* φ")

    result = (x % euler + euler) % euler
    return result


def gcd_ext(a, b):
    if not b:
        return 1, 0, a
    y, x, g = gcd_ext(b, a % b)
    return x, y - (a // b) * x, g


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
    test_rsa()
