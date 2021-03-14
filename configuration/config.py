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


class MeasurementConfig(BaseConfig):

    def __init__(self, meas_type: str = None):
        self.meas_type = meas_type
        self.meas_dict = self.load_measure_dict()
        if self.meas_type:
            self.meas_type_lname = self.meas_dict[self.meas_type]
        self.measrc = pkgr.resource_filename(__name__, 'measurerc.json')
        try:
            with open(self.measrc, 'r') as f:
                self.all_meas_params = json.load(f)
        except FileNotFoundError:
            self.all_meas_params = {}
            self.write_measrc(self.all_meas_params)
        if self.meas_type_lname:
            try:
                self.params = self.all_meas_params[
                    self.meas_type_lname
                ]
            except KeyError:
                self.params = {}
                self.all_meas_params[self.meas_type_lname] = self.params
                self.write_measrc(self.all_meas_params)

    @staticmethod
    def load_measure_dict():
        measure_dict_name = "measure_dict.json"
        measure_dict_path = pkgr.resource_filename(__name__, measure_dict_name)
        with open(measure_dict_path, 'r') as js:
            meas_dict = json.load(js)
        return meas_dict

    def write_measrc(self, content: Dict):
        with open(self.measrc, 'w') as f:
            json.dump(content, f, indent=4)


config_base = BaseConfig()
