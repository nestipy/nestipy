from litestar.params import Body as LBody, Parameter as LParam, Dependency as LDepends
from fastapi.params import Body as FBody, Param as FParam, Depends as FDepends, Header as FHeader


class Body:
    def __new__(cls, *args, **kwargs):
        return cls
