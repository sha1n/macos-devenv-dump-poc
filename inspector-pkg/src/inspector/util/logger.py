import logging
import logging.handlers as handlers
from abc import abstractmethod
from typing import Any

_ERASE_LINE = '\x1b[2K'


class Logger(object):

    @abstractmethod
    def progress(self, message): pass

    @abstractmethod
    def debug(self, message): pass

    @abstractmethod
    def info(self, message): pass

    @abstractmethod
    def warn(self, message): pass

    @abstractmethod
    def error(self, message): pass

    @abstractmethod
    def success(self, message): pass

    @abstractmethod
    def failure(self, message): pass

    @abstractmethod
    def command_info(self, command): pass

    @abstractmethod
    def command_output(self, output): pass


class ConsoleLogger(Logger):
    def __init__(self, level=logging.INFO):
        self.logger = logging.getLogger("console")
        self.logger.handlers.clear()
        stream_handler = logging.StreamHandler()
        stream_handler.terminator = ""
        self.logger.addHandler(stream_handler)
        self.logger.setLevel(level)

    def progress(self, message):
        if self.logger.level == logging.DEBUG:
            term = "\n"
        else:
            term = "\r"

        self.logger.info(msg="{}- \033[0;37;40m{}\033[0;0m{}".format(_ERASE_LINE, message, term))

    def debug(self, message):
        self.logger.debug("{}- \033[0;37;40m{}\033[0;0m\n".format(_ERASE_LINE, message))

    def info(self, message):
        self.logger.info("{}- \033[1;37;40m{}\033[0;0m\n".format(_ERASE_LINE, message))

    def warn(self, message):
        self.logger.warning("{}- \033[1;33;40m{}\033[0;0m\n".format(_ERASE_LINE, message))

    def error(self, message):
        self.logger.error("{}- \033[1;31;40m{}\033[0;0m\n".format(_ERASE_LINE, message))

    def success(self, message):
        self.logger.info("{}- \033[0;30;42m{}\033[0;0m\n".format(_ERASE_LINE, message))

    def failure(self, message):
        self.logger.error("{}- \033[1;31;40m{}\033[0;0m\n".format(_ERASE_LINE, message))

    def command_info(self, command):
        self.logger.info(
            msg="-\t ~ \033[1;37;40m \033[0;33;40m{}\033[0;0m\n"
                .format(command))

    def command_output(self, output):
        self.logger.info(output.strip())


class FileLogger(Logger):

    def __init__(self, filename, level=logging.INFO):
        file_handler = handlers.RotatingFileHandler(filename=filename, mode="a", maxBytes=1024 * 1000, backupCount=3)
        file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))

        self.logger = logging.getLogger("file")
        self.logger.setLevel(level)
        self.logger.addHandler(file_handler)

    def progress(self, message):
        self.logger.info(message)

    def debug(self, message):
        self.logger.debug(message, exc_info=self._exc_info(message))

    def info(self, message):
        self.logger.info(message)

    def warn(self, message):
        self.logger.warning(message, exc_info=self._exc_info(message))

    def error(self, message):
        self.logger.error(message, exc_info=self._exc_info(message))

    def success(self, message):
        self.logger.info(message)

    def failure(self, message):
        self.logger.error(message, exc_info=self._exc_info(message))

    def command_info(self, command):
        self.info("[Command]: {}".format(command))

    def command_output(self, output):
        self.logger.info(output.strip())

    @staticmethod
    def _exc_info(message):
        return isinstance(message, BaseException)


class NoopLogger(Logger):
    def __getattribute__(self, name: str) -> Any:
        return lambda *args, **kwrgs: None


class CompositeLogger(Logger):
    def __init__(self, *loggers: Logger):
        self.loggers = loggers

    def progress(self, message):
        self._all("progress", message)

    def debug(self, message):
        self._all("debug", message)

    def info(self, message):
        self._all("info", message)

    def warn(self, message):
        self._all("warn", message)

    def error(self, message):
        self._all("error", message)

    def success(self, message):
        self._all("success", message)

    def failure(self, message):
        self._all("failure", message)

    def command_info(self, command):
        self._all("command_info", command)

    def command_output(self, output):
        self._all("command_output", output)

    def _all(self, fn_name, *args, **kwargs):
        for logger in self.loggers:
            fn = getattr(logger, fn_name)
            fn(*args, **kwargs)


NOOP_LOGGER = NoopLogger()
