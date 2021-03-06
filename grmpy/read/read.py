"""The module contains the main function of the init file import process."""
import shlex
import os

from grmpy.check.check import check_initialization_dict
from grmpy.read.read_auxiliary import auxiliary
from grmpy.read.read_auxiliary import process


def read(file_):
    """The function reads the initialization file and returns a dictionary with parameters for the
    simulation.
    """
    if not os.path.isfile(file_):
        raise AssertionError()

    dict_ = {}
    for line in open(file_).readlines():

        list_ = shlex.split(line)

        is_empty = (list_ == [])

        if not is_empty:
            is_keyword = list_[0].isupper()
        else:
            is_keyword = False

        if is_empty:
            continue

        if is_keyword:
            keyword = list_[0]
            dict_[keyword] = {}
            continue

        process(list_, dict_, keyword)

    dict_ = auxiliary(dict_)

    # We perform some basic consistency checks regarding the user's request.
    check_initialization_dict(dict_)

    return dict_

