import numpy as np
from qcodes import (
    Station,
    Measurement,
    Instrument,
    load_or_create_experiment,
    initialise_or_create_database_at,
)
from qcodes.dataset.plotting import plot_dataset
from qcodes.tests.instrument_mocks import DummyInstrument
from sample import Sample, Chip, Device


def generate_CD_curr(Vg, Vsd, width=2, slope=20, smear=0.1):
    """
    Generate Coulomb Diamond current
    """
    Vgn = Vg - width * np.floor((Vg + width / 2) / width)
    print(Vgn)
    temp = np.abs(Vgn) - np.abs(Vsd / slope)
    print(temp)
    curr = 1 / (1 + np.exp(temp / smear))
    return curr


def load_or_create_dummy_instrument(name, **kwargs):
    if Instrument.exist(name):
        instr = Instrument.find_instrument(name)
        if Instrument.is_valid(instr):
            instrument = instr
        else:
            Instrument.close(instr)
            instrument = DummyInstrument(name, **kwargs)
    else:
        instrument = DummyInstrument(name, **kwargs)
    return instrument


class DummyStabilityDiagram(Measurement):
    def __init__(self, name="dummy stability diagram measurement"):
        super().__init__()
        self.sample = Sample(name="Test", log=False)
        self.chip = Chip("dummy chip", self.sample)
        self.device = Device("dumy device", self.sample, self.chip)

        # define the station and dummy instruments within class
        dac = load_or_create_dummy_instrument("dac", gates=["Vg", "Vsd"])
        dmm = load_or_create_dummy_instrument("dmm", gates=["current"])
        self.station = Station(dac, dmm)
        self.dac, self.dmm = dac, dmm

        # initialise database, experiment
        self.device.create_database()
        self.experiment = load_or_create_experiment(
            experiment_name="test", sample_name=self.sample.name
        )
        self.register_parameter(self.dac.Vg)
        self.register_parameter(self.dac.Vsd)
        self.register_parameter(dmm.current, setpoints=(self.dac.Vg, self.dac.Vsd))

    def set_parameters(self, Vg_range, Vsd_range, width=2, slope=20, smear=0.1):
        self.params = dict(
            Vg_range=Vg_range,
            Vsd_range=Vsd_range,
            width=width,
            slope=slope,
            smear=smear,
        )

    def start_run(self):
        print("Measurement starts")

        Vg_list = np.linspace(*self.params["Vg_range"], 100)
        Vsd_list = np.linspace(*self.params["Vsd_range"], 100)

        with self.run() as datasaver:
            for vg in Vg_list:
                self.dac.Vg(vg)
                for vsd in Vsd_list:
                    self.dac.Vsd(vsd)
                    curr = generate_CD_curr(
                        Vg=vg,
                        Vsd=vsd,
                        width=self.params["width"],
                        slope=self.params["slope"],
                        smear=self.params["smear"],
                    )
                    datasaver.add_result(
                        (self.dac.Vg, vg), (self.dac.Vsd, vsd), (self.dmm.current, curr)
                    )

            self.dataset = datasaver.dataset

    def plot_ds(self):
        plot_dataset(self.dataset)
