# -*- coding: utf-8 -*-
"""
===============================================
A01. Event related fields

This code will generate ERFs in response to the
visual input.

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

# Average trials in conditions and plot
evoked_right = epochs['cue onset right'].copy().average(method='mean').filter(0.0,30).crop(-.2,.5)
epochs['cue onset right'].copy().filter(0.0,30).crop(-.2,.5).plot_image(picks=['MEG1932'],
                                                                       vmin=-200, vmax=200)
evoked_right.copy().apply_baseline(baseline=(-.2,0))
evoked_right.copy().pick_types(meg='mag').plot_topo(title = 'Magnetometers')
evoked_right.plot_topomap(.1, ch_type='mag', time_unit='s')

evoked_right.copy().pick_types(meg='grad').plot_topo(title = 'Gradiometers',
                                                     merge_grads=True)
evoked_right.plot_topomap(.1, ch_type='grad', time_unit='s')

# Explore the whole dataset
resampled_epochs = epochs.copy().resample(200)
resampled_epochs.plot_psd(fmin=1.0, fmax=30.0, average=True,
                spatial_colors=False)  # explore the frequency content of the epochs
resampled_epochs.plot_psd_topomap(ch_type='grad', 
                                  normalize=False)  # spatial distribution of the PSD
                                                    # averaged across epochs and freqs













