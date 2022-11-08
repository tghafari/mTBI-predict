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
    1) read raw file with bids
    
Issues/ contributions to community:
    1) mne.read_epochs with preload=True raises 
    an [Erno 22] invalid argument, error
    
Questions:
    1) 

"""

import os.path as op
import os

import mne


# fill these out
site = 'Birmingham'
subject = '1'  # subject code in mTBI project
session = '01'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'P' # is the data collected 'P'ilot or 'T'ask?
task = 'SpAtt'
file_extension = '.fif'
file_suffix_epochd = '-epo'
file_suffix_evokd = '-ave'

# Specify specific file names
bids_root = r'Z:\MEG_data\MNE-bids-data-anonymized'  # RDS folder for bids formatted data
deriv_root = op.join(bids_root, 'derivatives', 'flux-pipeline' )  # RDS folder for results
deriv_folder = op.join(deriv_root , 'sub-' + subject, 'task-' + task)    
bids_fname = op.join('sub-' + subject + '_ses-' + session + '_task-' + task + 
                     '_run-' + run)  # define the ica cleaned file name
mne_read_epochs_fname = op.join(deriv_folder, bids_fname + file_suffix_epochd + file_extension)
evoked_fname = op.join(deriv_folder, bids_fname + file_suffix_evokd + file_extension)

report_root = r'Z:\Projects\mTBI predict\Results - Outputs\mne Reports'  # RDS folder for results
if not op.exists(op.join(report_root , 'sub-' + subject, 'task-' + task)):
    os.makedirs(op.join(report_root , 'sub-' + subject, 'task-' + task))
report_folder = op.join(report_root , 'sub-' + subject, 'task-' + task)

report_fname = op.join(report_folder, 'report_evokeds.html')

# Read epoched data
epochs = mne.read_epochs(mne_read_epochs_fname, verbose=True, preload=True)

# Make evoked data for conditions of interest and save
evoked_right = epochs['cue onset left'].copy().average(method='mean').filter(0.0,50).crop(-.2,.5)  # the cues are fliped for P103
evoked_left = epochs['cue onset right'].copy().average(method='mean').filter(0.0,50).crop(-.2,.5)
evokeds = [evoked_right, evoked_left]

mne.write_evokeds(evoked_fname, evokeds, verbose=True)

# Generate report
report = mne.Report(title='Evoked')
report.add_evokeds(evokeds=evokeds, 
                   titles=['cue right',
                           'cue left'],
                   n_time_points=10)
report.save(report_fname, overwrite=True, open_browser=True)

# Plot evoked data
epochs['cue onset right'].copy().filter(0.0,30).crop(-.2,.5).plot_image(picks=['MEG1932'],
                                                                       vmin=-200, vmax=200)
evoked_right.copy().apply_baseline(baseline=(-.2,0))
evoked_right.copy().pick_types(meg='mag').plot_topo(title = 'Magnetometers')
evoked_right.plot_topomap(.1, ch_type='mag', time_unit='s')

evoked_right.copy().pick_types(meg='grad').plot_topo(title = 'Gradiometers',
                                                     merge_grads=True)
evoked_right.plot_topomap(.1, ch_type='grad', time_unit='s')

# Explore the epoched dataset
resampled_epochs = epochs.copy().resample(200)
resampled_epochs.plot_psd(fmin=1.0, fmax=30.0, average=True,
                spatial_colors=True)  # explore the frequency content of the epochs
resampled_epochs.plot_psd_topomap(ch_type='grad', 
                                  normalize=False)  # spatial distribution of the PSD
                                                    # averaged across epochs and freqs











