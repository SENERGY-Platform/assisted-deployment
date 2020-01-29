__all__ = ('getLogger', )


from .configuration import config
from os import getcwd
import logging


logging_levels = {
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
    'debug': logging.DEBUG
}

color_code = {
    'CRITICAL': '\033[41m',
    'ERROR': '\033[31m',
    'WARNING': '\033[33m',
    'DEBUG': '\033[94m',
}


class LoggerError(Exception):
    pass


class ColorFormatter(logging.Formatter):
    def format(self, record):
        s = super().format(record)
        if record.levelname in color_code:
            return '{}{}{}'.format(color_code[record.levelname], s, '\033[0m')
        return s


if not config.Logger.level in logging_levels.keys():
    err = "unknown log level '{}'".format(config.Logger.level)
    raise LoggerError(err)


msg_fmt = '%(asctime)s - %(levelname)s: [%(name)s] %(message)s'
date_fmt = '%m.%d.%Y %I:%M:%S %p'


if config.Logger.to_file:
    handler = logging.FileHandler('{}/storage/assistant.log'.format(getcwd()))
    handler.setFormatter(logging.Formatter(fmt=msg_fmt, datefmt=date_fmt))
else:
    handler = logging.StreamHandler()
    if config.Logger.colored:
        handler.setFormatter(ColorFormatter(fmt=msg_fmt, datefmt=date_fmt))
    else:
        handler.setFormatter(logging.Formatter(fmt=msg_fmt, datefmt=date_fmt))


logger = logging.getLogger('assistant')
logger.propagate = False
logger.addHandler(handler)


logger.setLevel(logging_levels[config.Logger.level])


def getLogger(name: str) -> logging.Logger:
    return logger.getChild(name)
