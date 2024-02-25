import inspect

from peewee import TextField, IntegerField, MySQLDatabase

from peewee import Model as BaseModel


def Model(cls):
    class_attrs = {}
    for name, value in inspect.getmembers(cls):
        if not name.startswith('__'):
            class_attrs[name] = value
    class_attrs['Meta'] = type('Meta', (), {'database': db, 'db_table': str(cls.__name__).lower()})
    return type(cls.__name__, (BaseModel,), class_attrs)


db = MySQLDatabase('pesty', host='localhost', port=3306, user='root', password='')


@Model
class User:
    name = TextField()
    city = TextField()
    age = IntegerField()


# metaclass = type('Meta', (), {'database': db, 'db_table': str(User.__name__).lower()})
# User.Meta = metaclass

db.connect()
db.create_tables([User])
db.close()


# class User(BaseModel):
#     name = TextField()
#     city = TextField()
#     age = IntegerField()
#
#     class Meta:
#         database = db
#         db_table = User.__name__.lower()
