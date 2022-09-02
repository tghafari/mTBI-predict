# -*- coding: utf-8 -*-
"""
===============================================
06. Annotation of artifacts

This code will identify artifacts and then annotate
them for later use (eg., to reject).

written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:
    1)
    2) 
    
Issues:
    1) many of the blinks are not identified by find_eog_events
    2) hEOG is flat in sub=03
    3) read-Raw-bids doesn't work on the derivatives
    folder -> using mne_io_read_raw_fif instead
    4) get_bids_path_from_fname cannot recognize
    bids root from sss file
    5) BIDSPath doesn't read sss as suffix
    
Questions:
    1) why blink_onsets has -0.25?
    2) what exactly is raw.first_time?

"""

import os.path as op
import numpy as np

import mne
from mne.preprocessing import annotate_muscle_zscore

# fill these out
site = 'Birmingham'
subject = '03'  # subject code in mTBI project
session = '01'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'P' # is the data collected 'P'ilot or 'T'ask?
task = 'SpAtt'
file_extension = '.fif'
file_suffix = '-sss'

# specify specific file names
bids_root = r'Z:\MEG_data\MNE-bids-data'  # RDS folder for bids formatted data
deriv_root = op.join(bids_root, 'derivatives', 'flux-pipeline' )  # RDS folder for results
deriv_folder = op.join(deriv_root , 'sub-' + subject, 'task-' + task)
bids_fname = op.join('sub-' + subject + '_ses-' + session + '_task-' + task + 
                     '_run-' + run)  # define the max filtered file name
mne_read_raw_fname = op.join(deriv_folder, bids_fname + file_suffix + file_extension)

# read max filtered data 
raw_sss = mne.io.read_raw_fif(mne_read_raw_fname, preload=True)  # read_raw_bids doesn't work on derivatives

# Identifying and annotating eye blinks using vEOG
eog_events = mne.preprocessing.find_eog_events(raw_sss, ch_name='EOG001')
onset = eog_events[:,0] / raw_sss.info['sfreq'] -.25 #'from flux pipline, but why?'
                                                     # 'blink onsets in seconds'
onset -= raw_sss.first_time  # first_time is apparently the time start time of the raw data
n_blinks = len(eog_events)  # length of the event file is the number of blinks in total
duration = np.repeat(.5, n_blinks)  # duration of each blink is assumed to be 500ms
description = ['blink'] * n_blinks
annotation_blink = mne.Annotations(onset, duration, description)

# Identifying and annotating muscle artifacts
""" 
muscle artifacts are identified from the magnetometer data filtered and 
z-scored in filter_freq range
"""
threshold_muscle = 10
min_length_good = .2
filter_freq = [110,140]
annotation_muscle, scores_muscle = annotate_muscle_zscore(
    raw_sss, ch_type='mag', threshold=threshold_muscle, 
    min_length_good=min_length_good, filter_freq=filter_freq)
annotation_muscle.onset -= raw_sss.first_time  # align the artifact onsets to data onset
annotation_muscle._orig_time = None  # remove date and time from the annotation variable

# Include annotations in dataset and inspect
raw_sss.set_annotations(annotation_blink + annotation_muscle)
raw_sss.set_channel_types({'EOG001':'eog', 'EOG002':'eog'})  # set both vEOG and hEOG as EOG channels
eog_picks = mne.pick_types(raw_sss.info, meg=False, eog=True)
scale = dict(eog=500e-6)
raw_sss.plot(order=eog_picks, scalings=scale, start=50)

# Save the artifact annotated file
raw_sss.save(op.join(deriv_folder, bids_fname + file_suffix + '-ann' + 
                     file_extension), overwrite=True)




















