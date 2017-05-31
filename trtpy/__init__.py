# -*- coding: utf-8 -*-
"""
TRT Python Library
"""
import pkg_resources
import logging

try:
    __version__ = pkg_resources.get_distribution(__name__).version
except:
    __version__ = 'unknown'

def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logging.basicConfig(format="%(levelname)-8s\033[1m%(name)-21s\033[0m: %(message)s")
    logging.addLevelName(logging.WARNING,
        "\033[1;31m{:8}\033[1;0m".format(logging.getLevelName(logging.WARNING)))
    logging.addLevelName(logging.ERROR,
        "\033[1;35m{:8}\033[1;0m".format(logging.getLevelName(logging.ERROR)))
    logging.addLevelName(logging.INFO,
        "\033[1;32m{:8}\033[1;0m".format(logging.getLevelName(logging.INFO)))
    logging.addLevelName(logging.DEBUG,
        "\033[1;34m{:8}\033[1;0m".format(logging.getLevelName(logging.DEBUG)))
