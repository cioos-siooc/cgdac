import os
from abc import ABC
from typing import Any


def get_files(file_dir):
    """
    return all files under dir
    :param dir:
    :return:
    """
    paths = []
    if os.path.isdir(file_dir):
        for file in os.listdir(file_dir):
            file_path = os.path.join(file_dir, file)
            if os.path.isfile(file_path):
                paths.append(file_path)
    return paths


def convert_list_to_str(files: list or str) -> str:
    """convert a list of files name to a string

    ["name1","name2"] -> "/name1 /name2"
    """
    file_lists_str = ""
    if type(files) is str:
        return path_complement(files)
    for result in files:
        file_lists_str = file_lists_str + path_complement(result) + " "
    return file_lists_str


def path_complement(file: str, folder: bool = False) -> str:
    """To check is give path a absolute path format"""
    if not file.startswith("/"):
        file = '/' + file

    if folder:
        if not file.endswith('/'):
            file = file + '/'
    else:
        if file.endswith('/'):
            file = file[:-1]
    return file


class WrapperProxy(ABC):
    """proxy for wrapped object

    Subclass can access all public variable or public method from wrapped object

    overwrite the _setup method to get wrapped obj
    """

    def __init__(self, decorator=None) -> None:
        self.decorator = decorator
        self.__wrapped = self._setup()

    def _setup(self) -> object:
        raise NotImplementedError

    def __getattr__(self, item) -> Any:
        try:
            res = self.__getattribute__(item)
        except AttributeError:
            if item.startswith("_"):
                raise AttributeError
            res = getattr(self.__wrapped, item)
            if callable(res) and self.decorator is not None:
                res = self.decorator(res)
        return res
