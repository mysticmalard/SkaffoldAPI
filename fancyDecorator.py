# Decorator that allows optionally naming the filling
def _fancyDecorator(deco: function):
    # deco: main decorator function
        # _kern
    # Wrapper Function
    def wrapper(bar: str | function | type):
        # either
        # bar: name to be inherited
        # or
        # bar: filling
            # 'read'
            # listen
        name = '' # name to be inherited
        def make(baz: function | type):
            return deco(name, baz)
        if isinstance(bar, str):
            name = bar
            return make
        elif callable(bar):
            name = bar.__name__
            return make(bar)
        else:
            raise TypeError
    return wrapper