from typing import Any

text: str = "Rudro"


class City:
    def __init__(self, name: str, population: int) -> None:
        self.name = name
        self.population = population


Dhaka = City("Dhaka", 8900000)

city_temp: tuple[str, int] = (Dhaka.name, Dhaka.population)
print(city_temp)

number: int | float = 10.5

number: int | float = 10.5

numbers: list[int | float] = [1, 2.5, 3, 4.5]

fruits: tuple[str, str, str] = ("apple", "banana", "cherry")


users: dict[str, Any] = {
    "name": "Rudro",
    "age": 25,
    "is_active": True,
}


def root(num: int | float) -> float:
    return pow(num, 0.5)


rooted_num: float = root(12.5)
print(rooted_num)
