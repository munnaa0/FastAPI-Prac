
#Below function doesn't accept any argument
def fence(func):
    def wrapper(text: str):
        print("Before the function is called.")
        func(text)
        print("After the function is called.")

    return wrapper

# A decorator function will always return afunction. In this case, the wrapper function is returned.

# The following decorator func will accept an argument and will return a function.
def custom_fence(fences: str = "### "):
    def decorator(func):
        def wrapper(text: str):
            print(f" {fences}" * 10)
            func(text)
            print(f" {fences}" * 10)

        return wrapper

    return decorator

# This is testing without any argument in the decorator function
@fence
def name(name: str) -> None:
    print(f"My name is {name}")

@custom_fence("=== ")
def name2(name: str) -> None:
    print(f"My name is {name}")


name("Munna")
print("\n")
print("Without any argument in the decorator function")
print("\n")
name2("Munna")