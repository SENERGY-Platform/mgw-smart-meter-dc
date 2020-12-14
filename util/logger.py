"""
   Copyright 2020 InfAI (CC SES)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

__all__ = ("getLogger", "initLogger")


import logging


logging_levels = {
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
    'debug': logging.DEBUG
}


class LoggerError(Exception):
    pass


msg_fmt = '%(asctime)s - %(levelname)s: [%(name)s] %(message)s'
date_fmt = '%m.%d.%Y %I:%M:%S %p'


handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(fmt=msg_fmt, datefmt=date_fmt))

logger = logging.getLogger("smart-meter-dc")
logger.propagate = False
logger.addHandler(handler)


def initLogger(level):
    if level not in logging_levels.keys():
        err = "unknown log level '{}'".format(level)
        raise LoggerError(err)
    logger.setLevel(logging_levels[level])


def getLogger(name: str) -> logging.Logger:
    return logger.getChild(name)
