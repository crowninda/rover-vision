import logging
def setup_logger(log_file):
    # 配置日誌設置
    logging.basicConfig(level=logging.INFO,
                        format = '%(asctime)s - %(levelname)s - %(filename)s - %(message)s',
                        filename = log_file, 
                        filemode = 'a')

    # 創建並返回一个日誌實例
    return logging.getLogger("my_logger")