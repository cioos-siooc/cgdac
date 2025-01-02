import os
import glob


def get_latest_nc_file(full_path):
    '''
    Returns the lastest netCDF file found in the directory

    :param str root: Root of the directory to scan
    '''
    list_of_files = glob.glob('{}/*.nc'.format(full_path))
    if not list_of_files:  # Check for no files
        return None
    return max(list_of_files, key=os.path.getmtime)
