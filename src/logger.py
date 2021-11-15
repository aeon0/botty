import logging
import io
import os
import sys
import re
import warnings

class Logger:
    """Manage logging"""
    _logger_level = None
    _formatter = logging.Formatter('[%(asctime)s] %(levelname)-10s %(message)s')
    _log_contents = io.StringIO()
    _current_log_file_path = "info.log"
    _output = ""  # intercepted output from stdout and stderr
    string_handler = None
    file_handler = None
    console_handler = None
    logger = None

    @staticmethod
    def debug(data: str):
        if Logger.logger is None:
            Logger.init()
        Logger.logger.debug(data)
    
    @staticmethod
    def info(data: str):
        if Logger.logger is None:
            Logger.init()
        Logger.logger.info(data)

    @staticmethod
    def warning(data: str):
        if Logger.logger is None:
            Logger.init()
        Logger.logger.warning(data)

    @staticmethod
    def error(data: str):
        if Logger.logger is None:
            Logger.init()
        Logger.logger.error(data)

    @staticmethod
    def init(lvl = logging.DEBUG):
        """
        Setup logger for StringIO, console and file handler
        """
        Logger._logger_level = lvl

        if Logger.logger is not None:
            Logger.logger.warning("WARNING: logger was setup already, deleting all previously existing handlers")
            for hdlr in Logger.logger.handlers[:]:  # remove all old handlers
                Logger.logger.removeHandler(hdlr)

        # Create the logger
        Logger.logger = logging.getLogger("botty")
        for hdlr in Logger.logger.handlers:
            Logger.logger.removeHandler(hdlr)
        Logger.logger.setLevel(Logger._logger_level)
        Logger.logger.propagate = False

        # Setup the StringIO handler
        Logger._log_contents = io.StringIO()
        Logger.string_handler = logging.StreamHandler(Logger._log_contents)
        Logger.string_handler.setLevel(Logger._logger_level)

        # Setup the console handler
        Logger.console_handler = logging.StreamHandler(sys.stdout)
        Logger.console_handler.setLevel(Logger._logger_level)

        # Setup the file handler
        Logger.file_handler = logging.FileHandler(Logger._current_log_file_path, 'a')
        Logger.file_handler.setLevel(Logger._logger_level)

        # Optionally add a formatter
        Logger.string_handler.setFormatter(Logger._formatter)
        Logger.console_handler.setFormatter(Logger._formatter)
        Logger.file_handler.setFormatter(Logger._formatter)

        # Add the handler to the logger
        Logger.logger.addHandler(Logger.string_handler)
        Logger.logger.addHandler(Logger.console_handler)
        Logger.logger.addHandler(Logger.file_handler)
        
        # redirect stderr & stdout to logger, e.g. print("...")
        # would have to implement all the std func such as write() flush() etc.
        # sys.stderr = Logger
        # sys.stdout = Logger

    @staticmethod
    def remove_file_logger(delete_current_log: bool = False):
        """
        Remove the file logger to not write output to a log file
        """
        Logger.logger.removeHandler(Logger.file_handler)
        if delete_current_log and os.path.exists(Logger._current_log_file_path):
            try:
                os.remove(Logger._current_log_file_path)
            except PermissionError:
                warnings.warn("Could not remove info.log, permission denied")
