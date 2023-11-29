import logging
def setup_logger(log_file):
    
    # configuration of log settings 
    logging.basicConfig(level=logging.INFO,
                        format = '%(asctime)s - %(levelname)s - %(filename)s - %(message)s',
                        filename = log_file, 
                        filemode = 'a')

    # create and return a log instance
    return logging.getLogger("my_logger")