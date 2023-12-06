
import logging
from autoclass import autoargs
from os import makedirs
from datetime import datetime
from ..models import NewsDB, Log

import pyrootutils
ROOT_PROJ = pyrootutils.setup_root(
    search_from=__file__,
    indicator=".project-root",
    project_root_env_var=True,
    dotenv=True,
    pythonpath=True,
    cwd=True,
)

ROOT_LOG = ROOT_PROJ / 'logs'

class DbLogger:
    log_type = "file"

    @autoargs
    def __init__(self, name, root_log=ROOT_LOG):
        self.__logger = get_logger_as[self.log_type](name, root_log)

    def __call__(self, level, message='', data=None, not_db=False):
        if not_db: return None
        with NewsDB._meta.database.atomic():
            log = Log.create(
                level    = level,
                name     = self.name,
                message  = message if message else None,
                data     = data,
                datetime = datetime.now(), )
        return log

    def critical(self, message='', data=None, not_db=False):
        self.__logger.critical(message)
        return self("CRITICAL", message, data, not_db)
    
    def error(self, message='', data=None, not_db=False):
        self.__logger.error(message)
        return self("ERROR", message, data, not_db)
    
    def warning(self, message='', data=None, not_db=False):
        self.__logger.warning(message)
        return self("WARINING", message, data, not_db)
        
    def info(self, message='', data=None, not_db=False):
        self.__logger.info(message)
        return self("INFO", message, data, not_db)

    def debug(self, message='', data=None, not_db=False):
        self.__logger.debug(message)
        return self("DEBUG", message, data, not_db)


def get_logger_file(
        name     = 'UNKNOWN',
        root_log = ROOT_LOG,  ):

    logger = logging.getLogger(name)

    makedirs(root_log, exist_ok=True)

    formatter = logging.Formatter(
        '%(asctime)s:%(module)s:%(levelname)s:%(message)s',
        '%Y-%m-%d %H:%M:%S')

    today = datetime.now().strftime("%Y%m%d")

    # INFO 레벨 이상의 로그를 콘솔에 출력하는 Handler
    console_handler = logging.FileHandler(root_log / f"{name}_{today}_info.log", encoding='UTF-8')
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ERROR 레벨 이상의 로그를 `error.log`에 출력하는 Handler
    file_error_handler = logging.FileHandler(root_log / f"{name}_{today}_error.log", encoding='UTF-8')
    file_error_handler.setLevel(logging.ERROR)
    file_error_handler.setFormatter(formatter)
    logger.addHandler(file_error_handler)

    return logger

def get_logger(
        name     = 'UNKNOWN',
        root_log = ROOT_LOG,  ):

    # 로그 생성
    logger = logging.getLogger(name)

    # 로그의 출력 기준 설정
    logger.setLevel(logging.INFO)

    # log 출력 형식
    formatter = logging.Formatter(
        '%(asctime)s:%(module)s:%(levelname)s:%(message)s',
        '%Y-%m-%d %H:%M:%S')

    # log 출력
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger

get_logger_as = {
    'console': get_logger,
    'file' : get_logger_file
}