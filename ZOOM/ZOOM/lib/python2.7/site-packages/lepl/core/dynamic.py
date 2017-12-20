

class BaseVar(object):

    def __init__(self, value=None):
        if value is not None: value = self._cast(value)
        self.value = value

    def _cast(self, value):
        return value

    def setter(self):
        def wrapper(results):
            self.value = self._cast(results[0])
            return results
        return wrapper

    def __lt__(self, other):
        return self.value < other

    def __le__(self, other):
        return self.value <= other

    def __gt__(self, other):
        return self.value > other

    def __ge__(self, other):
        return self.value >= other

    def __eq__(self, other):
        return self.value == other

    def __hash__(self):
        return hash(self.value)


class IntVar(BaseVar):

    def _cast(self, value):
        return int(value)

    def __int__(self):
        return self.value
