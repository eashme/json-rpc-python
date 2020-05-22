def get_key(mp: dict, *keys):
    for key in keys:
        try:
            mp = mp[key]
        except KeyError:
            return None
    return mp


if __name__ == '__main__':
    m = {"a": 1, "b": 2, "c": {"d": {"f": 11}}}
    assert get_key(m, "c", "d", "f") == 11
