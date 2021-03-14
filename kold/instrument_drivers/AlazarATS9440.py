from qcodes.instrument_drivers.AlazarTech.ATS9440 import AlazarTech_ATS9440
from qcodes.instrument_drivers.AlazarTech.ats_api import AlazarATSAPI
from qcodes.instrument_drivers.AlazarTech.ATS import AlazarTech_ATS, \
    AcquisitionController
from qcodes.instrument_drivers.AlazarTech.utils import TraceParameter
import numpy as np
from typing import Any, Optional, Dict, Union


class AlazarATS9440(AlazarTech_ATS9440):
    """
    This driver is only for configure the Alazar card. Create the 
    AlazarATS9440_AcquisitionController object then read date using 
    self.controller.read().
    """

    def __init__(self, name: str,
                 dll_path: str,
                 **kwargs):
        super().__init__(name, dll_path, **kwargs)
        self.controller = None

    def set_record_size(self, record_size: Union[list, tuple]):
        if len(record_size) != 2:
            raise ValueError("The length of record size should be 2")
        pre_trig_sps, post_trig_sps = record_size
        self.api.set_record_size(self._handle,
                                 pre_trigger_samples=pre_trig_sps,
                                 post_trigger_samples=post_trig_sps)

    def set_parameters(self, **kwargs):
        for key, value in kwargs.items():
            if not key in self.parameters.keys():
                raise KeyError(f"The parameter {key} does not exist in \
                    AlazarTech_ATS9440 driver")
        self.param_kwargs = kwargs
        return self.param_kwargs

    def configure(self, **kwargs):
        kws = self.param_kwargs or self.set_parameters(**kwargs)
        with self.syncing():
            # first set the default values
            self.clock_source('INTERNAL_CLOCK')
            self.clock_edge('CLOCK_EDGE_RISING')
            self.sample_rate(1_000_000)
            self.channel_selection('A')
            self.mode('NPT')
            self.coupling1('DC')
            self.channel_range1(1)  # 1 V
            self.impedance1(50)  # 50 Ohm
            for param, value in kws.items():
                self.set(param, value)


class ATSAPI_Plus(AlazarATSAPI):

    # add the method for single port acquisition mode

    pass


class AlazarATS9440_AcquisitionController(AcquisitionController):
    def __init__(self, name: str,
                 alazar_name: str,
                 acq_mode='dual port',
                 **kwargs: Any):
        super().__init__(name, alazar_name, **kwargs)
        self.acq_mode = acq_mode
        self.acq_kwargs: Dict[str, Any] = {}
        self.buffer: Optional[np.ndarray] = None
        self.num_of_channels = 1
        self.add_parameter('read', get_cmd=self._read)
        setattr(self._get_alazar(), 'controller', self)

    def _read(self):
        if self.acq_mode == 'dual port':
            value = self._get_alazar().acquire(acquisition_controller=self,
                                               **self.acq_kwargs)
        elif self.acq_mode == 'single port':
            pass
        return value

    def update_acq_kwargs(self, **kwargs):
        self.acq_kwargs.update(**kwargs)

    def pre_start_capture(self) -> None:
        alazar = self._get_alazar()
        self.samples_per_record = alazar.samples_per_record()
        self.records_per_buffer = alazar.records_per_buffer()
        self.buffers_per_acquisition = alazar.buffers_per_acquisition()
        self.buffer = np.zeros(self.samples_per_record *
                               self.records_per_buffer *
                               self.num_of_channels)

    def pre_acquire(self):
        pass

    def handle_buffer(self, data: np.ndarray,
                      buffer_number: Optional[int] = None):
        assert self.buffer is not None
        self.buffer += data

    def post_acquire(self):
        assert self.buffer is not None
        alazar = self._get_alazar()
        # average all records in a buffer
        records_per_acquisition = (1. * self.buffers_per_acquisition *
                                   self.records_per_buffer)
        record = np.zeros(self.samples_per_record)
        for i in range(self.records_per_buffer):
            i0 = i * self.samples_per_record
            i1 = i0 + self.samples_per_record
            record += self.buffer[i0:i1] / records_per_acquisition

        return alazar.signal_to_volt(1, record + 127.5)
