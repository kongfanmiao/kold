import os
import sys
import time



# Create the Sample, Chip, Device


# Set parameters

measurement_choice  = 'SD'
integration_time  = 5e-3 
ramp_to_zero_Vg_B   = [False,False] 


    
Vg_range       = [-3.2, -4]     # V because of Vg_gain, but the output of the DAC is actually in mV's note 0.8 to 0.72
Vsd_range      = [-50, 50]      # mV!
dVsd           = 0.075         # mV

Vg_numpoints   = 20*16 -1       # inf for max allowed resolution
Vsd_numpoints  = 20*16 -1       # inf for max allowed resolution

####################
    # IVVI Parameters: #
    ####################
    

Vg_gain                     = 5*1e-3     # V/mV (15, 30 or 45 V/V for S1h, 1e-3 if directly connnected via the DAC, 5 prefix for S1f postamps)
Vsd_divider                 = .1               # mV/mV  set on the IVVI Rack (on the rack is V/V) [1. (DAC) or .1 (100m) .01 (10m) .001 (1m) on S3b]
voltage_meas_gain           = 1.             # 1V/1e-6A   
current_gain                = 1         # current amplifier gain set on IVVI box (M1b module) (1e6 to 1e9) 


#####################
    # Field Parameters: #
    #####################
'''
Field Direction, Starting Value (rad)
Theta is the angle with X direction in XY plane, Phi the angle with Z
B*cos(T)*sin(P),B*sin(T)*sin(P), B*cos(P)]
'''
B_range         =       [1, 1]              # [Bstart, Bstop]; in case of rotation [Brho] only. BTFC takes first value only and sweeps to it.
B_numpoints     =       10                # automatically adds 1 point to have the extrema; 360
sweep_rate      =       0.01                #0.125 max rate through zero
parameter       =       'Sweep'              # either 'Sweep', 'Phi' (Z plane), or 'Theta' (XY plane)
Theta           =       +0.      * (pi/2)  # Theta = 0 is X, Theta = pi/2 is Y,
Phi             =       +1.      * (pi/2)  # Phi = pi/2 is in the XY plane
tot_angle_rotation  =   +0.      * (pi/2)  # in case of rotation, specify the total angle

MC_temp_threshold   = False                # this is the MC temp in mK the script wait before meas. False to skip
check_interval      = 100                  # this is used just for the continuous measures, and it's the number of measure before checking meausre



# Create experiment, instruments, station, and measurement

# transport experiment

# station



# method: check num_points


# triton driver

# ivvi driver

# alazar driver

# zurich driver



# start measurement

















