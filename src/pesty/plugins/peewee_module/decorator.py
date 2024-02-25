from peewee import Model as BaseModel


def Model(cls) -> BaseModel:
    setattr(cls, 'peewee_model__', True)
    return cls
