"""file system controllers"""
import abc
import tarfile
import os

from functools import partial
from typing import (
    Any,
    Callable,
)

from .utils import WrapperProxy
from .linux_command import LinuxCommand
from .remote_server_connector import RemoteServer
from .loacl_command_executor import execute_local_command


class LinuxFileSystemController(WrapperProxy):
    """Abstract class for file system controller"""

    def __init__(self) -> None:
        self._un_commit_list = []
        self._result_cache = []
        super().__init__(self.send_decorate)

    def _setup(self) -> LinuxCommand:
        """
        Setup linux commands
        :return:
        """
        return LinuxCommand()

    def send(self, command: str) -> None:
        """
        Save the command into the un commit list
        :param command:
        :return:
        """
        if self._result_cache:
            self._result_cache = []
        self._un_commit_list.append(command)

    def send_decorate(self, func: Callable[..., str]) -> Callable[[Any], str]:
        """
        This decorator is used to decorate all function in the object created by _setup function
        """

        def the_send(self_obj: LinuxFileSystemController, *args: Any, **kwargs: Any):
            res = func(*args, **kwargs)
            self_obj.send(res)
            return res

        the_send_with_self = partial(the_send, self)
        return the_send_with_self

    @abc.abstractmethod
    def commit(self, parallel=True) -> None:
        """
        Commit the commands in the commit list
        :return:
        """
        ...

    def get_result(self) -> list:
        return self._result_cache


class LocalLinuxFileSystemController(LinuxFileSystemController):
    """Run commands on local linux server"""
    command_execute_function = execute_local_command

    def __init__(self, user: str = None, host: str = None) -> None:
        super().__init__()
        self.user = user
        self.host = host

    def commit(self, parallel: bool = True, timeout=None) -> None:
        execute_local_command(parallel, self._un_commit_list, self._result_cache, timeout=timeout)
        self._un_commit_list = []

    @staticmethod
    def uncompress_files(file_path: str, path_to_extractdir: str = None):
        with tarfile.open(file_path, "r:bz2") as tar:
            if path_to_extractdir:
                extractdir = path_to_extractdir
            else:
                extractdir = os.path.dirname(file_path)
            tar.extractall(extractdir)
        return extractdir

    def remove_files_under_target_dir(self, target_dir: str):
        # todo can become a command as well
        if os.path.isdir(target_dir):
            for the_file in os.listdir(target_dir):
                file_path = os.path.join(target_dir, the_file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    pass


class RemoteLinuxFileSystemController(LinuxFileSystemController):
    """Run command on remote linux server"""
    RemoteServerClass = RemoteServer

    def __init__(self, host: str, user: str, password: str = None, port: int = 22) -> None:
        super().__init__()
        self.user = user
        self.host = host
        self.port = port
        self.remote_server = self.RemoteServerClass(user, host, password, port)

    def back_up_remote_dir(self, abs_dir: str) -> None:
        back_up_dir = abs_dir + ".bak"
        self.move_files(abs_dir, back_up_dir)
        self.commit()

    def commit(self, parallel: bool = True) -> None:
        with self.remote_server as remote_server_handler:
            for command in self._un_commit_list:
                ouput_res = remote_server_handler.send_command(command)
                self._result_cache.append(ouput_res)
        self._un_commit_list = []

    def get_result_list(self) -> list:
        ret_list = []
        for binary_ret in self.get_result():
            ret_str = binary_ret.decode("utf-8")
            ret_str_list = ret_str.splitlines()
            ret_list.append(ret_str_list)
        return ret_list
