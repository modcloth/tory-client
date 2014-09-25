# vim:fileencoding=utf-8

import argparse


def kvpair(string):
    return string.strip().split('=', 1)


def stringified_dict(indict):
    return dict(
        ((str(key), str(value)) for key, value in indict.items())
    )


class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                    argparse.RawDescriptionHelpFormatter):
    pass
