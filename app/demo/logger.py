import logging.config


def singleton(cls):
    instances = {}

    def get_instance() -> dict:
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return get_instance()


@singleton
class Logger:
    def __init__(self):
        self.logger = logging.getLogger('__name__')
        self.logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(ch)
