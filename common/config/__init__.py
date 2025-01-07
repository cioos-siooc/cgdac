"""For non-Docker environments, this module loads all variables from
 a file and creates a configuration dictionary. For Docker environments,
it reads variables from the system, verifies that all required variables are present,
 and stores them in a configuration dictionary for later use."""


import os
from dotenv import load_dotenv
from ..utils import check_create_dir

CURRENT_DIR = os.path.dirname(__file__)
# Get the parent directory (one level up)
parent_dir = os.path.dirname(CURRENT_DIR)

# Get the grandparent directory (two levels up)
PROJECT_DIR = os.path.dirname(parent_dir)

DOCKER_DIR = os.path.join(PROJECT_DIR, 'docker')

DOT_ENV_PATH = os.path.join(DOCKER_DIR, '.env')
DOT_EXAMPLE_PATH = os.path.join(DOCKER_DIR, '.env.example')

if os.path.exists(DOT_ENV_PATH):
    load_dotenv(dotenv_path=DOT_ENV_PATH)


def check_env_variables(example_path):
    """
    Check if all variables in .env.example are available in the environment.
    Convert boolean-like variables to actual booleans.
    Return a dictionary of required variables with their values.
    """
    required_vars = {}

    try:
        with open(example_path, 'r') as file:
            for line in file:
                line = line.strip()

                # Skip comments and empty lines
                if line.startswith("#") or not line:
                    continue

                # Extract the variable key
                key = line.split('=', 1)[0].strip()

                # Get the variable value from the environment
                value = os.getenv(key)

                # Convert to boolean if applicable
                if value is not None and value.lower() in ('true', 'false'):
                    if value.lower() == 'false':
                        value = False
                    else:
                        value = True

                required_vars[key] = value
    except FileNotFoundError:
        print(f"Error: {example_path} not found.")
        return None

    # Print missing variables for debugging
    missing_vars = {k: v for k, v in required_vars.items() if v is None}
    if missing_vars:
        print(f"Missing environment variables: {', '.join(missing_vars.keys())}")
    else:
        print("All environment variables are available.")

    return required_vars




PROJECT_NAME = "cgdac"
USER_DIR = os.path.expanduser("~")
RESOURCE_DIR = check_create_dir(os.path.join(USER_DIR, "resource"))
PROJECT_RESOURCE_DIR = check_create_dir(os.path.join(RESOURCE_DIR, PROJECT_NAME))
DICT_CONFIG = check_env_variables(DOT_EXAMPLE_PATH)
