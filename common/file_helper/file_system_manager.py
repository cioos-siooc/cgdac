from .file_system_controller import LocalLinuxFileSystemController, RemoteLinuxFileSystemController


class FileSystemManager:
    def __init__(self):
        self._local = LocalLinuxFileSystemController()

    @property
    def local(self):
        return self._local

    def load(self, host, username, password=None, controller_tag=None):
        remote_linux_file_system_controller = RemoteLinuxFileSystemController(host, username, password)
        if not controller_tag:
            controller_tag = host

        if not hasattr(self, controller_tag):
            setattr(self, controller_tag, remote_linux_file_system_controller)
        else:
            msg = "the controller {} was already registered".format(controller_tag)
            raise AttributeError(msg)
