import logging
import argparse
import sys

class CustomLogFormatter(logging.Formatter):
    """ Format the logging better with a customised log formatter """

    cyan = "\x1b[34m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    orange = "\x1b[38;5;214m"
    red = "\x1b[38;5;202m"
    reset = "\x1b[0m"
    fmat = "%(asctime)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"


    FORMATS = {
        logging.DEBUG: cyan + fmat + reset,
        logging.INFO: grey + fmat + reset,
        logging.WARNING: yellow + fmat + reset,
        logging.ERROR: orange + fmat + reset,
        logging.CRITICAL: red + fmat + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt='%d-%m-%Y %H:%M:%S')
        return formatter.format(record)
    

class CustomArgparseFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    """ Format the argparse helper message better with a customised argparse formatter """

    def _get_help_string(self, action):
        help_msg = action.help
        if '%(default)' not in action.help:
            if action.default is not argparse.SUPPRESS:
                defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    if isinstance(action.default, type(sys.stdin)):
                        help_msg += ' [default: ' + str(action.default.name) + ']'
                    elif action.default is not None:
                        help_msg += f' [default: {", ".join([str(i) for i in action.default])}]'
        return help_msg
