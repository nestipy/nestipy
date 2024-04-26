class A:
    pass


class B(A):
    pass


if __name__ == "__main__":
    b = B()
    assert isinstance(b, A)
