import uuid

APP_GUARD = "__APP__GUARD__"
APP_FILTER = "__APP__FILTER__"
APP_INTERCEPTOR = "__APP__INTERCEPTOR__"


class _AppKey:
    @property
    def APP_GUARD(self):
        return APP_GUARD + uuid.uuid4().hex

    @property
    def APP_FILTER(self):
        return APP_FILTER + uuid.uuid4().hex

    @property
    def APP_INTERCEPTOR(self):
        return APP_INTERCEPTOR + uuid.uuid4().hex


AppKey = _AppKey()
