from typing import List

from common.file_helper.file_system_controller import \
    LocalLinuxFileSystemController as BaseLocalLinuxFileSystemController
from common.file_helper.file_system_controller import RemoteLinuxFileSystemController


class SvcServerController(RemoteLinuxFileSystemController):
    def __init__(self, user: str, host: str, config: dict, port: int):
        super().__init__(host, user, port=port)
        self.config = config

    def get_result_list(self) -> list:
        ret_list = []
        for binary_ret in self.get_result():
            ret_str = binary_ret.decode("utf-8")
            ret_str_list = ret_str.splitlines()
            ret_list.append(ret_str_list)
        return ret_list

    def find_all_bad_files(self) -> List[str]:
        command = "find {} -name \"badFiles.nc\"".format(self.config["cache_dataset_path"])
        self.script(command)
        self.commit()
        ret = self.get_result_list()
        return ret

    def get_file_modified(self, file_path):
        command = "stat -c %Y {}".format(file_path)
        self.script(command)
        self.commit()
        ret = self.get_result_list()
        return ret


class DownloadHandler(BaseLocalLinuxFileSystemController):
    """
    This handler run command on local server mainly focus on upload files to remote server
    """

    def __init__(self, user: str, host: str, port: int = 22):
        super().__init__()
        self.user = user
        self.host = host
        self.port = port

    def upload_file_to_erddap(self, file_path: str, dest_path: str):
        return self.scp_file(file_path, dest_path, user=self.user, host=self.host, folder=False, upload=True,
                             port=self.port)

    def download_file_from_erddap(self, file_path: str, dest_path: str):
        return self.scp_file(file_path, dest_path, user=self.user, host=self.host, folder=False, upload=False,
                             port=self.port)


class FileSystemControllerFactory:
    """
    Factory to craft the file controllers
    """

    def __init__(self, setting):
        self.setting = setting

    def get_controller(self, name: str):
        name_lower = name.lower()
        if name_lower == "svc_server_controller":
            return SvcServerController(self.setting.SVC_SERVER["user"], self.setting.SVC_SERVER["host"],
                                       self.setting.SVC_SERVER,
                                       self.setting.SVC_SERVER["port"])
        elif name_lower == "svc_download_controller":
            return DownloadHandler(self.setting.SVC_SERVER["user"], self.setting.SVC_SERVER["host"],
                                   self.setting.SVC_SERVER["port"])


