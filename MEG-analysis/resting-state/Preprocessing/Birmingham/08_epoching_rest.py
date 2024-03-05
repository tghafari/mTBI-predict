# -*- coding: utf-8 -*-
"""
===============================================
08. Epoching raw data based on conditions

This code will epoch continuous MEG signal based
on conditions saved in stim channel and generates 
an HTML report about epochs.

written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:
    1) which epochs to keep?
    
Issues/ contributions to community:
    
Questions:

"""

import os.path as op
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import mne
from mne_bids import BIDSPath, read_raw_bids

# fill these out
site = 'Birmingham'
subject = '2001'  # subject code in mTBI project
session = '02B'  # data collection session within each run
run = '01'  # data collection run for each participant
task = 'rest'
meg_extension = '.fif'
meg_suffix = 'meg'
input_suffix = 'ica'
deriv_suffix = 'epo'

using_events_csv = False  # for when we are not using events_from_annotation. default is False

rprt = True  # do you want to generate mne report?

# Specify specific file names
data_root = r'Z:\Projects\mTBI-predict\collected-data'
bids_root = op.join(data_root, 'BIDS', 'task_BIDS')  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, 
                     suffix=meg_suffix, extension=meg_extension)

raw = read_raw_bids(bids_path=bids_path, verbose=False, 
                     extra_params={'preload':True})  # read raw for events and event ids only

deriv_folder = op.join(bids_root, 'derivatives', 'sub-' + subject, 
                       'task-' + task)  # RDS folder for results
bids_fname = bids_path.basename.replace(meg_suffix, input_suffix)  # only used for suffices that are not recognizable to bids 
input_fname = op.join(deriv_folder, bids_fname)
deriv_fname = str(input_fname).replace(input_suffix, deriv_suffix)


# read raw and events file
raw_ica = mne.io.read_raw_fif(input_fname, allow_maxshield=True,
                              verbose=True, preload=True)

# Set the peak-peak amplitude threshold for trial rejection.
""" subject to change based on data quality"""
reject = dict(grad=5000e-13,  # T/m (gradiometers)
              mag=5e-12,      # T (magnetometers)
              #eog=150e-6      # V (EOG channels)
              )

epochs = mne.make_fixed_length_epochs(raw_ica,   # not setting meta data is ok
                                  duration=5.0, 
                                  preload=False, 
                                  reject_by_annotation=True, 
                                  proj=True, overlap=0.0, 
                                  id=1, verbose=None)

############################### Check-up plots ################################
# Plotting to check the raw epoch
epochs.load_data()
epochs.copy().filter(0, 60).plot(n_epochs=10)  # shows all the events in the epoched data that's based on 'cue_onset_left'

# plot amplitude on heads
times_to_topomap = [.1, .8, 1.1]
epochs.copy().filter(0, 60).pick('meg').average().plot_topomap(times_to_topomap) 

# Topo plot evoked responses
mne.viz.plot_evoked_topo(epochs.copy().filter(0, 60).pick('meg').average(), show=True)

fig_bads = epochs.plot_drop_log()  # rejected epochs
###############################################################################

# Plots the average of one epoch type - pick best sensors for report
epochs.pick('grad').copy().filter(0, 60).average().plot() 

# Plots to save
fig_left = epochs.copy().filter(0.0,60).crop(-.1,1.2).plot_image(
    picks=['MEG1943'],vmin=-100,vmax=100)  # event related field image
fig_right = epochs.copy().filter(0.0,60).crop(-.1,1.2).plot_image(
    picks=['MEG2522'],vmin=-100,vmax=100)  # event related field image

# Save the epoched data and generate report
#epochs.save(deriv_fname, overwrite=True)

if rprt:
   report_root = r'Z:\Projects\mTBI-predict\results-outputs\mne-reports'  # RDS folder for reports
   report_folder = op.join(report_root , 'sub-' + subject, 'task-' + task)
   report_fname = op.join(report_folder, 
                          f'mneReport_sub-{subject}_{task}.hdf5')    # it is in .hdf5 for later adding images
   html_report_fname = op.join(report_folder, f'report_preproc_{task}.html')
   
   report = mne.open_report(report_fname)
   report.add_figure(fig=fig_right, title='right sensor',
                     caption='fixed-length evoked response on one right sensor (MEG2522) - filter 0-60Hz', 
                     tags=('epo'),
                     section='epocheds' 
                     )   
   report.add_figure(fig=fig_left, title='left sensor',
                     caption='fixed-length evoked response on one left sensor (MEG1943) - filter 0-60Hz', 
                     tags=('epo'),
                     section='epocheds'
                     )
   report.save(report_fname, overwrite=True, open_browser=True)
   report.save(html_report_fname, overwrite=True, open_browser=True)  # to check how the report looks
