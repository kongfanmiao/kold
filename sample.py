import os
import json

from qcodes.dataset.sqlite.database import initialise_or_create_database_at
from configuration.config import config_base

from qcodes.utils.helpers import named_repr

from typing import Union


class Sth:
    def __init__(self, create_dir=True):
        self.path = config_base["root_dir"]

    def create_directory(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)
            msg = "{} directory {} created".format(self.__class__.__name__, self.path)
            print(msg)

    def __repr__(self):
        return named_repr(self)


class Sample(Sth):
    def __init__(self, name, create_dir=True, log=True):
        super().__init__()
        self.name = name
        self.path = self.get_path()
        if create_dir:
            self.create_directory()
        self.chips = []
        self.devices = {}
        self.log = log

        self.log_path = os.path.join(self.path, "devices_log.json")
        try:
            with open(self.log_path) as fp:
                dvs = json.load(fp)
                self.chips = list(dvs.keys())
                self.devices = dvs
        except FileNotFoundError:
            # log file does not exist
            if log:
                self.log_devices()

    def get_path(self):
        return os.path.join(config_base["root_dir"], self.name)

    def log_devices(self):
        with open(self.log_path, "w") as fp:
            dvs_new = {}
            for ch, dvs in self.devices.items():
                dvs_new[ch] = list(dvs)
            json.dump(dvs_new, fp, indent=4)
        msg = "Devices logged"
        print(msg)


class Device(Sth):
    def __init__(self, name, sample, chip, create_dir=True):
        super().__init__()
        self.name = name
        if isinstance(sample, Sample):
            self.sample = sample
        elif isinstance(sample, str):
            self.sample = Sample(name=sample)
        if isinstance(chip, Chip):
            self.chip = chip
        elif isinstance(chip, str):
            self.chip = Chip(name=chip, sample=self.sample)
        if self.name not in self.chip.devices:
            self.chip.add_device(self, log=self.sample.log)
        self.path = self.get_path()
        if create_dir:
            self.create_directory()

    def get_path(self):
        return os.path.join(
            config_base["root_dir"], self.sample.name, self.chip.name, self.name
        )

    def create_database(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path, exist_ok=True)
        db_file = "_".join((self.sample.name, self.chip.name, self.name)) + ".db"
        db_path = os.path.join(self.path, db_file)
        initialise_or_create_database_at(db_path)


class Chip(Sth):
    def __init__(self, name, sample, create_dir=True):
        super().__init__()
        self.name = name
        if isinstance(sample, Sample):
            self.sample = sample
        elif isinstance(sample, str):
            self.sample = Sample(name=sample)
        self.sample = sample
        self.path = self.get_path()
        if self.name in self.sample.chips:
            self.devices = self.sample.devices[self.name]
        else:
            # new chip
            self.devices = []
            self.sample.chips.append(self.name)
            self.sample.devices[self.name] = self.devices
            if self.sample.log:
                self.sample.log_devices()

        if create_dir:
            self.create_directory()

    def get_path(self):
        return os.path.join(config_base["root_dir"], self.sample.name, self.name)

    def add_device(self, device, log=True):
        if isinstance(device, Device):
            self.devices.append(device.name)
        elif isinstance(device, str):
            self.devices.append(device)
        self.sample.devices[self.name] = self.devices
        if log:
            self.sample.log_devices()

