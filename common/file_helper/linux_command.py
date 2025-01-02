"""Linux system commands wrapped by Python code"""
import os
from .utils import path_complement, convert_list_to_str

REMOTE_USER_HOST = "{user}@{remote_host}"


class LinuxCommand:

    @staticmethod
    def make_directory(abs_dir: str) -> str:
        return "mkdir -p {}".format(abs_dir)

    @staticmethod
    def list_files(abs_dir: str = None) -> str:
        if abs_dir:
            return "ls {}".format(abs_dir)
        else:
            return "ls"

    @staticmethod
    def create_file(abs_file_path: str) -> str:
        return 'touch {file_path}'.format(file_path=abs_file_path)

    @staticmethod
    def change_directory(abs_dir: str) -> str:
        return 'cd {}'.format(abs_dir)

    @staticmethod
    def move_files(abs_path, target_path) -> str:
        return "mv {} {}".format(abs_path, target_path)

    @staticmethod
    def remove_file(abs_path: str, directory=False):
        if directory:
            return "rm -r {}".format(abs_path)
        else:
            return "rm {}".format(abs_path)

    @staticmethod
    def bash_script(abs_path: str) -> str:
        return "bash {}".format(abs_path)

    @staticmethod
    def whoami() -> str:
        return "whoami"

    @staticmethod
    def current_path() -> str:
        return "pwd"

    #
    # @staticmethod
    # def compress_files(file_dir_or_files_list, result_path, res_name):
    #     """Linux command for compress one file or a list of files
    #     """
    #     file_input_type = type(file_dir_or_files_list)
    #     basic_command_format = "tar -cjvf {} {}"
    #     result_path = os.path.join(result_path, res_name)
    #     if file_input_type is str:
    #         return basic_command_format.format(result_path, file_dir_or_files_list)
    #     elif file_input_type is list:
    #         return basic_command_format.format(result_path, convert_list_to_str(file_dir_or_files_list))
    #     else:
    #         raise AttributeError(
    #             "file_dir_or_files_list:() must be file path, or a list of file path".format(file_dir_or_files_list))
    #
    # @staticmethod
    # def uncompress_files(file_path, path_to_extract_dir=None):
    #     """
    #     Uncompress the file
    #     """
    #     basic_command_format = "tar -xzvf {} {}"
    #     if path_to_extract_dir:
    #         extractdir = "-C {}".format(path_to_extract_dir)
    #     else:
    #         extractdir = ""
    #     return basic_command_format.format(file_path, extractdir)

    @staticmethod
    def copy_file(src_path: str, dst_dir: str, new_name=None):
        is_idr = False
        if src_path.endswith("/"):
            is_idr = True

        if not is_idr:
            if not new_name:
                name = os.path.basename(src_path)
                dst = os.path.join(dst_dir, name)
            else:
                dst = os.path.join(dst_dir, new_name)
        else:
            dst = dst_dir
        if is_idr:
            dir_option = " -R "
        else:
            dir_option = ""
        base_command_format = "cp {}{} {}"
        return base_command_format.format(dir_option, src_path, dst)

    @staticmethod
    def make_soft_link(src_path: str, dst_dir: str, new_name=None):
        is_idr = False
        if src_path.endswith("/"):
            is_idr = True

        if not is_idr:
            if not new_name:
                name = os.path.basename(src_path)
                dst = os.path.join(dst_dir, name)
            else:
                dst = os.path.join(dst_dir, new_name)
        else:
            dst = dst_dir

        base_command_format = "ln -s {} {}"
        return base_command_format.format(src_path, dst)

    @staticmethod
    def scp(para1: str, para2: str, options: str = None, port=22) -> str:
        if options:
            return "scp -P {port} {recursive} {para1} {para2}".format(para1=para1, para2=para2, recursive=options,
                                                                      port=port)
        else:
            return "scp -P {port} {para1} {para2}".format(para1=para1, para2=para2, port=port)

    @staticmethod
    def script(command: str):
        return command

    @staticmethod
    def scp_file(scp_from: str, scp_to: str, user: str, host: str, folder: bool = False,
                 upload: bool = True, port=22) -> str:
        """upload or download file/dir to or from remote server

        default is upload
        """
        if folder:
            recursive = "-r"
            scp_from = path_complement(scp_from)
        else:
            recursive = ""
        user_host = REMOTE_USER_HOST.format(user=user, remote_host=host, dst=scp_to)
        if upload:
            para1 = scp_from
            para2 = "{}:{}".format(user_host, scp_to)
        else:
            para1 = "{}:{}".format(user_host, scp_from)
            para2 = scp_to
        return LinuxCommand.scp(para1, para2, recursive, port)

    @staticmethod
    def scp_files(scp_from: str, scp_to: str, user: str, host: str, upload: bool = False, port=22) -> str:
        """upload or download files to or from remote server

        default is upload
        """
        user_host = REMOTE_USER_HOST.format(user=user, remote_host=host, dst=scp_to)
        scp_from = scp_from
        if upload:
            para1 = convert_list_to_str(scp_from)
            para2 = "{}:{}".format(user_host, scp_to)
        else:
            para1 = "{}:\"{}\"".format(user_host, convert_list_to_str(scp_from))
            para2 = scp_to
        return LinuxCommand.scp(para1, para2, port=port)

    @staticmethod
    def rsync(source: str, destination: str) -> str:
        return "rsync -a {source} {destination}".format(source=source, destination=destination)

    @staticmethod
    def rsync_file(rsync_from, rsync_to, user, host, upload=False):
        user_host = REMOTE_USER_HOST.format(user=user, remote_host=host, dst=rsync_to)
        scp_from = rsync_from
        if upload:
            para1 = convert_list_to_str(scp_from)
            para2 = "{}:{}".format(user_host, rsync_to)
        else:
            para1 = "{}:\"{}\"".format(user_host, convert_list_to_str(scp_from))
            para2 = rsync_to
        return LinuxCommand.rsync(para1, para2)

