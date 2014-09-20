# vim:fileencoding=utf-8


def stringified_dict(indict):
    return dict(
        ((str(key), str(value)) for key, value in indict.items())
    )
