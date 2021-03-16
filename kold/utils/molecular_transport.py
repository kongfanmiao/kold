import numpy as np
import matplotlib.pyplot as pp
import types
from scipy.special import expi
from scipy.constants import hbar, m_e, eV, elementary_charge, physical_constants

constants = types.SimpleNamespace(
    m_eff=1 * m_e,  # change 1 with the appropriate value --> effective mass
    a=10,  # lattice spacing in nm, in case transport simulation are requested
    hbar=hbar,
    eV=eV,
    meV=eV * 1e-3,
    e=elementary_charge,
)

# Defining custom unit is easy - just add attributes to the constants namespace
constants.kb_eV = physical_constants["Boltzmann constant in eV/K"][0]
constants.mu_B = physical_constants["Bohr magneton"][0] / constants.meV


def sperichal_to_cartesian(r, theta, phi):
    """ Convert spherical coordinates to Cartesian. """
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = (
        r * np.cos(theta) + 0 * phi
    )  # last term ensure all the three cartesian coordinates have the same dimensions
    return np.array([x, y, z]).T


class Landau_Buttiker:
    def __init__(self, **kwargs):
        self.Cleft = kwargs.get("left_capacitance", 1)
        self.Cright = kwargs.get("right_capacitance", 1)
        self.Cgate = kwargs.get("gate_capacitance", 1)
        self.Vsd = kwargs.get("Vsd", np.linspace(-0.5, 0.5005, 1_000))
        self.Vg = kwargs.get("Vg", np.linspace(-0.5, 0.5005, 1_000))


## Testing part ##
if __name__ == "__main__":

    print(constants.kb_eV)
    print(constants.m_eff)
    print(hasattr(constants, "kb_eV"))
