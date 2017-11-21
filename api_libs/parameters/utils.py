class ObjectDict(dict):
    '''Makes a dictionary behave like an object, with attribute-style access.
    from tornado.util
    '''
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value
