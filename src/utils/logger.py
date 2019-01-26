import logging

def get_logger (name: str, level = logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('../data/log/{0}.log'.format(name))
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(fh)
    return logger


