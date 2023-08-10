# -*- coding: utf-8 -*-
import logging
import logging.handlers

def is_empty(container):
    if container:
        return False
    else:
        return True

def is_str(obj):
    if isinstance(obj, basestring):
        return True
    return False

def in_list(ulist, str):
    for item in ulist:
        if item == str:
            return True
    return False

class applog:
    def __init__(self, appname):
        self.appname = appname
        self.__m_logger = logging.getLogger(self.appname)
        self.__m_logger.setLevel(logging.INFO)

        fmtstr = "%(asctime)-15s " + self.appname + "[%(process)d]: %(levelname)-6s %(message)s"
        dtfmtstr = '%b %d %H:%M:%S'
        formatter = logging.Formatter(fmt=fmtstr, datefmt=dtfmtstr)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.__m_logger.addHandler(handler)

    def getLogger(self):
        return self.__m_logger

    def resetHandler(self):
        handler = logging.handlers.SysLogHandler(address = '/dev/log',
                                                 facility=logging.handlers.SysLogHandler.LOG_LOCAL0)

        fmtstr = self.appname + "[%(process)d]: %(levelname)-s %(message)-s"
        formatter = logging.Formatter(fmtstr)
        handler.setFormatter(formatter)
        self.__m_logger.addHandler(handler)
