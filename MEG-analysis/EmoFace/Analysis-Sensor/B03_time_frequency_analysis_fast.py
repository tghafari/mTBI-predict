# -*- coding: utf-8 -*-
"""
===============================================
B02. Tiem frequency representation of power (high freq)

This code will calculate TFR of powe for each 
trial and then averages over trials to characterize 
the modulation of oscillatory activity > 30Hz. 

written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:
    1) 
    
Issues/ contributions to community:
    1) mne.read_epochs with preload=True raises 
    an [Erno 22] invalid argument, error
    
Questions:
    1) 

"""

import os.path as op
import numpy as np

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

# Set the parameters for fast frequencies and run for attention right and left
""" more spectral smoothing is required"""
freqs = np.arange(30, 101, 2)
n_cycles = freqs / 4  # shorter time window insures good temporal resolution
time_bandwidth = 4.0  # 'N=3 tapers, the resulting spectral smoothing'
                      # 'is at least 6Hz (bc. visual gamma is broad band)'

tfr_fast_left = mne.time_frequency.tfr_multitaper(epochs['cue onset left'],
                                                  freqs=freqs, n_cycles=n_cycles,
                                                  time_bandwidth=time_bandwidth,
                                                  picks='grad',
                                                  use_fft=True, return_itc=False,
                                                  average=True, decim=2,
                                                  n_jobs=4, verbose=True)  # 'jobs allows for parallel execution for'
                                                                           # 'multicore CPUs'
tfr_fast_right = mne.time_frequency.tfr_multitaper(epochs['cue onset right'],
                                                   freqs=freqs, n_cycles=n_cycles,
                                                   time_bandwidth=time_bandwidth,
                                                   picks='grad',
                                                   use_fft=True, return_itc=False,
                                                   average=True, decim=2,
                                                   n_jobs=4, verbose=True)  


# Use relative baseline 
tfr_fast_left.plot(picks=['MEG2112'], baseline=[-.5,-.125],
                   mode='percent', tmin=-.5, tmax=1.0,
                   title='MEG2112')
tfr_fast_right.plot(picks=['MEG1942'], baseline=[-.5,-.125],
                    mode='percent', tmin=-.5, tmax=1.0,
                    title='MEG1942')

# Plot TFR on whole head 
tfr_fast_left.plot_topo(tmin=-.5, tmax=1.0,
                        baseline=[-.5,-.125], mode='percent',
                        fig_facecolor='w', font_color='k',
                        title=['TFR of power > 30Hz-left'])
tfr_fast_right.plot_topo(tmin=-.5, tmax=1.0,
                         baseline=[-.5,-.3], mode='percent',
                         fig_facecolor='w', font_color='k',
                         title=['TFR of power > 30Hz-right'])
# Plot gamma topographically
tfr_fast_left.plot_topomap(tmin=0.0, tmax=.6,
                           fmin=60, fmax=90,
                           baseline=[-.5,-.125], mode='percent',
                           vmin=-.1, vmax=.1,
                           title='attention left')
tfr_fast_right.plot_topomap(tmin=0.0, tmax=.6,
                           fmin=60, fmax=90,
                           baseline=[-.5,-.125], mode='percent',
                           vmin=-.1, vmax=.1,
                            title='attention right')

# Compare power modulation for attention right and left (always R- L)
tfr_slow_lateralization_power= tfr_fast_left.copy()
tfr_slow_lateralization_power.data = (tfr_fast_right.data - tfr_fast_left.data) / (tfr_fast_right.data + tfr_fast_left.data)
tfr_slow_lateralization_power.plot_topo(tmin=-.5, tmax=0.0,
                                        fig_facecolor='w', font_color='k',
                                        title='attention right - attention left')
tfr_slow_lateralization_power.plot_topomap(tmin=0.0, tmax=.6, fmin=60, fmax=90)


































