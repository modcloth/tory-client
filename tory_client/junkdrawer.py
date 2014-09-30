# vim:fileencoding=utf-8
import argparse
import datetime


DEFAULT_SINCE = (
    datetime.datetime.utcnow() - datetime.timedelta(days=30)
).isoformat() + 'Z'


def kvpair(string):
    return string.strip().split('=', 1)


def stringified_dict(indict):
    return dict(
        ((str(key), str(value)) for key, value in indict.items())
    )


class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                    argparse.RawDescriptionHelpFormatter):
    pass
