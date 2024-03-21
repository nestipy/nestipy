import abc


class MethodTrackerMeta(type):
    def __new__(cls, name, bases, dct):
        new_class = super().__new__(cls, name, bases, dct)
        for method_name in new_class.__dict__:
            method = getattr(new_class, method_name)
            if callable(method) and method_name != "specific_method":
                setattr(new_class, method_name, cls.track_method_call(method))
        return new_class

    @staticmethod
    def track_method_call(method):
        def wrapper(instance, *args, **kwargs):
            if method.__name__ == "specific_method":
                parent_method = getattr(super(instance.__class__, instance), "parent_method")
                parent_method(*args, **kwargs)
            print(f"Method {method.__name__} was called with args: {args}, kwargs: {kwargs}")
            return method(instance, *args, **kwargs)

        return wrapper


class Parent(metaclass=MethodTrackerMeta):

    @abc.abstractmethod
    def pp(self):
        pass

    def parent_method(self):
        pass


class C:
    pass


class Child(C, Parent):

    def pp(self):
        pass

    def specific_method(self):
        print("Child method logic")


# Exemple d'utilisation
if __name__ == "__main__":
    child = Child()
    child.specific_method()
