# -*- coding: utf-8 -*-


class Mock(object):
    def __getattr__(self, attr):
        pass


class Internal(object):
    def __init__(self, foo=None):
        self.data = foo

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, name):
        return self.data.__getitem__(name)

    def __setitem__(self, name, value):
        return self.data.__setitem__(name, value)

    def get(self, value, default=None):
        return self.data.get(value, default)
