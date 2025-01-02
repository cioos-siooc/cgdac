import os
import shutil

from pathlib import Path
from ceotr_common_utilities.file_prepare import check_create_dir

def find_yml_file_name(folder_path):
    # Function to find YAML file names in a given folder
    name_list = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".yml"):
            name_list.append(file_name)
    return name_list


def cp_tpl_yml(source_path, destination_folder):
    # Function to copy a template YAML file to a destination folder
    source_file_name = Path(source_path).stem
    rename_file_name = source_file_name[:-4] + ".yml"
    destination_path = os.path.join(destination_folder, rename_file_name)
    shutil.copyfile(source_path, destination_path)


def check_dataset_yml_config_files(target_folder):
    # Function to check and copy template YAML files to a target folder
    yml_template_folder = os.path.dirname(os.path.abspath(__file__))
    check_create_dir(target_folder)
    # Find YAML files in the current path (presumably the template files)
    tpl_files = find_yml_file_name(yml_template_folder)

    # Find YAML files in the target folder
    target_folder_yml_files = find_yml_file_name(target_folder)

    # Iterate over the template files
    for tpl_name in tpl_files:

        # Check if the template file starts with any existing YAML file name
        #todo: bugs, if exist don't recreate!!!!!!!!!!!
        if not any(tpl_name.startswith(existing_file.split('.')[0]) for existing_file in target_folder_yml_files):

            # Construct the template path
            tpl_path = os.path.join(yml_template_folder, tpl_name)

            # Check if the target folder exists
            if os.path.exists(target_folder):
                try:
                    cp_tpl_yml(tpl_path, target_folder)
                except FileNotFoundError:
                    # If system can't find the destination folder, create one and try again
                    os.makedirs(target_folder)
                    cp_tpl_yml(tpl_path, target_folder)

# Example usage:
# check_dataset_yml_config_files("/path/to/target/folder")
