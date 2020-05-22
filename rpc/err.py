class ErrBaseClass(Exception):
    def __init__(self, parent, child):
        self.parent = parent
        self.child = child

    def __str__(self):
        return f"{self.child} not base on {self.parent}"


class ErrLackOfNecessaryKey(Exception):
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return f"lack of necessary key: {self.key}"


class ErrTargetMethodNotFound(Exception):
    def __init__(self, method_name: str):
        self.method_name = method_name

    def __str__(self):
        return f"method {self.method_name} Not Found on Rpc Server"


class ErrUnKnownParams(Exception):
    def __init__(self, params):
        self.params = params

    def __str__(self):
        return f"known params format : {self.params}"


def err_handler(rpc_method, kwargs, err) -> str:
    return f"rpc method : {rpc_method.method_name} , args:{args} , kwargs:{kwargs}  err: {err.__str__()}"
