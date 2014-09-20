# vim:fileencoding=utf-8


def kvpair(string):
    return string.strip().split('=', 1)


def stringified_dict(indict):
    return dict(
        ((str(key), str(value)) for key, value in indict.items())
    )
