"""Gunicorn *development* config file"""
import os
import multiprocessing
from common import check_create_dir
from common import PROJECT_NAME, PROJECT_RESOURCE_DIR, DICT_CONFIG
LOG_FOLDER = check_create_dir(os.path.join(PROJECT_RESOURCE_DIR, "log"))

DEPLOYMENT_ENVIRONMENT = os.environ.get("DEPLOYMENT_ENV", "dev")

if DEPLOYMENT_ENVIRONMENT == "dev":
    # The number of worker processes for handling requests
    workers = multiprocessing.cpu_count() * 2 + 1
    loglevel = 'info'

else:
    workers = 1
    loglevel = 'debug'


bind = "unix:/var/run/socket/{}.sock".format(PROJECT_NAME)

# Debugging
reload = False  # Restart workers when code changes (useful for development)
# Write access and error info to /var/log
accesslog = os.path.join(LOG_FOLDER, "access.log")
errorlog = '-'

# Logging configuration
logfile = os.path.join(LOG_FOLDER, "gunicorn_logs.log")
logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": logfile,
            "maxBytes": 1024*1024*100,  # 100MB
            "backupCount": 10,
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "gunicorn.error": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": True,
        },
        "gunicorn.access": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
    "root": {"level": "INFO", "handlers": ["console", "file"]},
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
        },
    },
}


# Redirect stdout/stderr to log file
capture_output = True
# Daemonize the Gunicorn process (detach & enter background)
daemon = False
worker_connections = 1000  # Max number of simultaneous clients for async workers
timeout = 30  # Workers silent for more than this many seconds are killed and restarted
keepalive = 2  # The number of seconds to wait for requests on a Keep-Alive connection

# Process naming
proc_name = PROJECT_NAME  # A base to use with setproctitle for process naming

# Server hooks
def on_starting(server):
    server.log.info("Server is starting...")