from peewee import TextField, IntegerField

from nestipy.plugins.peewee_module.decorator import Model


@Model
class User:
    name = TextField()
    city = TextField()
    age = IntegerField()
