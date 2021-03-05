import json
import os
import pkg_resources as pkgr
from typing import Dict



class BaseConfig():

    koldrc_name = "koldrc.json"

    def __init__(self):
        path = pkgr.resource_filename(__name__, self.koldrc_name)
        self.kold_defaults = self.load_config(path)

    
    @staticmethod
    def load_config(path: str):
        """
        Load configuration from json file
        """
        with open(path) as js:
            config = json.load(js)
        return config

    
    def write_config(self, path: str, config: dict):
        """
        Write the current configuration to given path
        """
        with open(path, "w") as js:
            json.dump(config, js, indent=4)
    

    def __getitem__(self, key: str):
        return dict.__getitem__(self.kold_defaults, key)

    
    def __setitem__(self, key: str, value):
        dict.__setitem__(self.kold_defaults, key, value)
    


class InstruemntConfig(BaseConfig):
    
    pass





config_base = BaseConfig()