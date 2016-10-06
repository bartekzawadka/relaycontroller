import logging
import logging.handlers
import os


class RelayLogger:

    @staticmethod
    def get_logger(modulename, logsdir):
        logger = logging.getLogger(name=modulename)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(RelayLogger.__get_handler(modulename, logsdir))
        return logger

    @staticmethod
    def __get_handler(modulename, logsdir):
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        if logsdir is None:
            logsdir = 'logs'

        if not os.path.exists(logsdir):
            os.makedirs(logsdir)

        handler = logging.handlers.TimedRotatingFileHandler(os.path.join(logsdir, modulename+'.log'), when="midnight")
        handler.suffix = "%Y-%m-%d"
        handler.setFormatter(formatter)
        return handler