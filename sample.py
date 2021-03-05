
from .configuration.config import config_base


class Sample():

    def __init__(self, name, path):
        self.name = name
        self.path = path

print(config_base['root_dir'])