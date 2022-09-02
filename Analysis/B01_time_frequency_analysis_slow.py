# -*- coding: utf-8 -*-
"""
===============================================
B01. Time frequency representation of power (low freq)

This code will calculate TFR of powe for each 
trial and then averages over trials to characterize 
the modulation of oscillatory activity < 30Hz. 
Also, modulation index is calculated.

written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:
    1) use anonymized data (sub =1)
    2) create a new script for modulation and
    lateralization indices
    
Issues/ contributions to community:
    1) mne.read_epochs with preload=True raises 
    an [Erno 22] invalid argument, error
    2) plot_topo should include a parameter 'ax'
    3) show=False does not work in plot_topo
    
Questions:
    1) alpha is low on both occipital cortices
    in attention left?

"""

import os.path as op
import numpy as np
import matplotlib.pyplot as plt

import mne

# fill these out
site = 'Birmingham'
subject = '03'  # subject code in mTBI project
session = '01'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'P' # is the data collected 'P'ilot or 'T'ask?
task = 'SpAtt'
file_extension = '.fif'
file_suffix = '-epo'

# Specify specific file names
bids_root = r'Z:\MEG_data\MNE-bids-data'  # RDS folder for bids formatted data
deriv_root = op.join(bids_root, 'derivatives', 'flux-pipeline' )  # RDS folder for results
deriv_folder = op.join(deriv_root , 'sub-' + subject, 'task-' + task)    
bids_fname = op.join('sub-' + subject + '_ses-' + session + '_task-' + task + 
                     '_run-' + run)  # define the ica cleaned file name
mne_read_epochs_fname = op.join(deriv_folder, bids_fname + file_suffix + file_extension)

# Read epoched data
epochs = mne.read_epochs(mne_read_epochs_fname, verbose=True)

# Set the parameters for slow freq analysis and run for attention left and right 
freqs = np.arange(2,31,1)  # the frequency range over which we perform the analysis
n_cycles = freqs / 2  # the length of sliding window in cycle units. 
time_bandwidth = 2.0  # '(2deltaTdeltaF) number of DPSS tapers to be used + 1.'
                      # 'it relates to the temporal (deltaT) and spectral (deltaF)' 
                      # 'smoothing'
                      # 'the more tapers, the more smooth'->useful for high freq data
picks='grad'  # all plots from tfrs will be on picks

tfr_slow_left = mne.time_frequency.tfr_multitaper(epochs['cue onset left'],
                                                  freqs=freqs, n_cycles=n_cycles,
                                                  time_bandwidth=time_bandwidth,
                                                  picks=picks,
                                                  use_fft=True, return_itc=False,
                                                  average=True, decim=2,
                                                  n_jobs=4, verbose=True)  # jobs allows for parallel execution for 
                                                                           # multicore CPUs
                                                
tfr_slow_right = mne.time_frequency.tfr_multitaper(epochs['cue onset right'],
                                                   freqs=freqs, n_cycles=n_cycles,
                                                   time_bandwidth=time_bandwidth,
                                                   picks=picks,
                                                   use_fft=True, return_itc=False,
                                                   average=True, decim=2,
                                                   n_jobs=4, verbose=True)
# Plot TFR on all sensors 
""" pick which sensors to show later""" 
tfr_slow_left.plot_topo(tmin=-.5, tmax=1.0, 
                        baseline=[-.5,-.3], mode='percent',
                        fig_facecolor='w', font_color='k',
                        vmin=-1, vmax=1, 
                        title='TFR of power < 30Hz-left')
tfr_slow_right.plot_topo(tmin=-.5, tmax=1.0,
                         baseline=[-.5,-.3], mode='percent',
                         fig_facecolor='w', font_color='k',
                         vmin=-1, vmax=1, 
                         title='TFR of power < 30Hz-right')

# Plot TFR for representative sensors
fig, axis = plt.subplots(2, 2, figsize = (7, 7))
sensors = ['MEG1733','MEG1942', 'MEG2333','MEG2342']

for sensor in sensors:
    if sensors.index(sensor) < len(sensors)/2:
        tfr_slow_right.plot(picks=sensor, baseline=[-.5,-.25],
                            mode='percent', tmin=-.5, tmax=1.0,
                            vmin=-.75, vmax=.75, 
                            axes=axis[sensors.index(sensor),1], show=False)
    else:   
        tfr_slow_left.plot(picks=sensor, baseline=[-.5,-.25],
                           mode='percent', tmin=-.5, tmax=1.0,
                           vmin=-.75, vmax=.75,
                           axes=axis[sensors.index(sensor)-2,0], show=False)
        
axis[0,0].set_title(' \nattention right-left sensors')
axis[0,1].set_title(' \nattention left-right sensors')

fig.set_tight_layout(True)
plt.show()                            
# Plot alpha topographically
""" fill tmin and tmax using the representative sensors"""

fig, axis = plt.subplots(1, 2, figsize=(7, 4))
tfr_slow_left.plot_topomap(tmin=.35, tmax=.75, fmin=9, fmax=12,
                           vmin=-.6, vmax=.6,
                           baseline=(-.5, -.3), mode='percent', axes=axis[0],
                           title='Left', show=False)
tfr_slow_right.plot_topomap(tmin=.35, tmax=.75, fmin=9, fmax=12,
                            vmin=-.6, vmax=.6,
                            baseline=(-.5, -.3), mode='percent', axes=axis[1],
                            title='Right', show=False)
fig.set_tight_layout(True)
plt.show()

# Compare power modulation for attention right and left (always R- L)
tfr_slow_modulation_power= tfr_slow_left.copy()
tfr_slow_modulation_power.data = (tfr_slow_right.data - tfr_slow_left.data) / (tfr_slow_right.data + tfr_slow_left.data)

tfr_slow_modulation_power.plot_topo(tmin=-.5, tmax=1.0, vmin=-.6, vmax=.6, 
                                    fig_facecolor='w', font_color='k',
                                    title='attention right - attention left')

tfr_slow_modulation_power.plot_topomap(tmin=-.35, tmax=.75, fmin=9, fmax=12, 
                                       vmin=-.2, vmax=.2,                                           
                                       title='alpha modulation index')
