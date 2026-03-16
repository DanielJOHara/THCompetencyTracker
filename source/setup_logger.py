"""This module sets up the logger for the TH Competency Tracker tool."""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from source.appdata import AppData


class StreamToLogger(object):
    """Fake file-like stream object that redirects writes to a logger instance.
       https://stackoverflow.com/questions/19425736/how-to-redirect-stdout-and-stderr-to-logger-in-python"""
    def __init__(self, logger: logging.Logger, level: int):
        self.logger = logger
        self.level = level
        self.linebuf = ''

    def write(self, buf: str):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.level, line.rstrip())

    def flush(self):
        pass


def setup_logger(ad: AppData) -> None:
    """ Set up a logger as defined in the options in the args object in the database object.
        It logs to a rotating file and to the console if it is running in console mode. If
        not in console mode stdout and stderr are redirected to the log file."""
    # Set logging level
    if ad.args.logging_level == 'DEBUG':
        logging_level = logging.DEBUG
    elif ad.args.logging_level == 'INFO':
        logging_level = logging.INFO
    elif ad.args.logging_level == 'WARNING':
        logging_level = logging.WARNING
    elif ad.args.logging_level == 'ERROR':
        logging_level = logging.ERROR
    elif ad.args.logging_level == 'CRITICAL':
        logging_level = logging.CRITICAL
    else:
        logging_level = logging.WARNING

    # Set logger
    logger = logging.getLogger()

    formatter = logging.Formatter(
        fmt='%(asctime)s : %(levelname)s : %(filename)s : %(funcName)s : %(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    # Setup log file with file rotation
    log_path = str(os.path.join(ad.args.logging_directory, ad.args.logging_file_name))
    file_handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=int(1E6), backupCount=5)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # If attached to console stream log there as well as to file
    if sys.stdin and sys.stdin.isatty():
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    else:
        # If not attached to console redirect stdout and stderr to logger
        print(f"logger {type(logger)} logging.INFO {type(logging.INFO)}")
        sys.stdout = StreamToLogger(logger, logging.INFO)
        sys.stderr = StreamToLogger(logger, logging.ERROR)

    logger.setLevel(logging_level)
