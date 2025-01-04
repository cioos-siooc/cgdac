import os
from .folder_clean_up import clean_folder





def check_create_dir(file_dir, recursively=False):
    """
    If dir exist just return the path, else create the dir and return the path
    """
    if not os.path.isdir(file_dir):
        if recursively:
            os.makedirs(file_dir)
        else:
            os.mkdir(file_dir)
    return file_dir
