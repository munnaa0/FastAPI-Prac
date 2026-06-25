text: str = "Rudro"


number: int | float = 10.5

number: int | float = 10.5


def root(num: int | float) -> float:
    return pow(num, 0.5)


rooted_num: float = root(12.5)
print(rooted_num)
