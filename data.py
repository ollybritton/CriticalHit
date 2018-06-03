from time import gmtime, strftime

LOG = True
DEBUG = True

LOG_PREFIX = "LOG"
DEBUG_PREFIX = "DEBUG"

DIE_TYPES = [
    4,
    6,
    8,
    10,
    12,
    20
]

STRING_DIE_TYPES = [
    "d4",
    "d6",
    "d8",
    "d10",
    "d12",
    "d20"
]


def log(string):
    if LOG:
        print("{} [{}]: {}".format(
            strftime("%Y-%m-%d %H:%M:%S", gmtime()), LOG_PREFIX, string))

    else:
        return


def debug(string):
    if DEBUG:
        print("{} [{}]: {}".format(
            strftime("%Y-%m-%d %H:%M:%S", gmtime()), DEBUG_PREFIX, string))

    else:
        return
