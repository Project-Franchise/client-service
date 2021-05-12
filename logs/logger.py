"""
File for setuping logger
"""
import logging
import sys

log_formatter = logging.Formatter(
    '%(asctime)s | [%(lineno)d]%(filename)s in %(funcName)s() -> [%(levelname)s]: %(message)s')


def setup_logger(logger_name, log_file, logging_level=logging.DEBUG):
    """
    Can setup as many loggers as you want
    """

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.DEBUG)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging_level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
