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
        self.Isd = kwargs.get("Isd", np.zeros([len(self.Vsd), len(self.Vg)]))

    def single_dot():
        pass

    def double_dot():
        pass


class Spectral_Density_Model:
    def __init__(self, **kwargs):
        self.w = kwargs.get(
            "w", np.linspace(1e-5, 0.03, 1_000)
        )  # frequency range for the B(t) integral
        self.J = kwargs.get("J", np.zeros(len(self.w)))
        self.E = kwargs.get("E", np.linspace(-0.1, 0.1, 1_000))
        self.time = kwargs.get(
            "time", np.linspace(0, 10_000, 1_000)
        )  # time range for one-sided Fourier Transform
        self.marcus_background = False
        self.modes = []
        self.specden = False

    def calculate_rate_constants(self, yL, yR, Tph=25 * 1e-3):
        """
        Calculate the hopping rates from the correlation function

        Parameters
        ----------
        yL : left molecule-lead coupling (eV)

        yR : right molecule-lead coupling (eV)

        Tph : Phononic Temperature (K) 
        """

        betaph = 1 / (constants.kb_eV * Tph)
        time = self.time
        Y = (yL + yR) / 2

        # Calculate correlation function
        self.B = np.empty(
            len(time), dtype=np.complex64
        )  # marginally faster than np.zeros

        for idx, t in enumerate(time):
            # single mode part
            D1 = (self.J / self.w ** 2) * (
                (np.cos(self.w * t) - 1) / np.tanh(betaph * self.w / 2)
                - 1j * np.sin(self.w * t)
            )

            self.B[idx] = np.exp(np.trapz(D1, self.w)) if self.specden else 1
            for mode in self.modes:
                omega, g = mode
                D2 = (g ** 2 / omega ** 2) * (
                    (np.cos(omega * t) - 1) / np.tanh(betaph * omega / 2)
                    - 1j * np.sin(omega * t)
                )
                self.B[idx] *= np.exp(D2)

        # include the lifetime broadening
        self.B *= np.exp(-Y * time)

        # compute the hopping rates from the correlation function
        kred, kox = [np.empty(len(self.E), dtype=np.complex64) for _ in range(2)]
        for idx, eps in enumerate(self.E):
            kred[idx] = np.trapz(np.exp(1j * time * eps) * self.B, time)
            kox[idx] = np.trapz(np.exp(-1j * time * eps) * self.B, time)

        self.k_ox = np.real(kox) * 2
        self.k_red = np.real(kred) * 2


## Testing part ##
if __name__ == "__main__":

    print(constants.kb_eV)
    print(constants.m_eff)
    print(hasattr(constants, "kb_eV"))
