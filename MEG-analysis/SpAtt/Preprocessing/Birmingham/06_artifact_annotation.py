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
    1) rename eog and ecg channels (if wrong names)
    2) run maxfilter on anonymized data before 
    reading them here
    
Issues:
    1) many of the blinks are not identified by find_eog_events
    2) there is no ecg or veog channgel for sub=03
    3) 

Contributions to community:
    1) read-Raw-bids doesn't work on the derivatives
    folder -> using mne_io_read_raw_fif instead
    2) get_bids_path_from_fname cannot recognize
    bids root from sss file
    3) BIDSPath doesn't read sss as suffix
    
Questions:
    1) why blink_onsets has -0.25?

"""

import os.path as op
import numpy as np

import mne
from mne.preprocessing import annotate_muscle_zscore
from mne_bids import BIDSPath

# fill these out
site = 'Birmingham'
subject = '2005'  # subject code in mTBI project
session = '04B'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'P' # is the data collected 'P'ilot or 'T'ask?
task = 'SpAtt'
meg_suffix = 'meg'
meg_extension = '.fif'
input_suffix = 'raw_sss'
deriv_suffix = 'ann'

remove_line_noise = False
platform = 'bluebear'  # are you using 'bluebear', 'mac', or 'windows'?

if platform == 'bluebear':
    rds_dir = '/rds/projects/j/jenseno-avtemporal-attention'
    camcan_dir = '/rds/projects/q/quinna-camcan/dataman/data_information'
elif platform == 'windows':
    rds_dir = 'Z:'
    camcan_dir = 'X:/dataman/data_information'
elif platform == 'mac':
    rds_dir = '/Volumes/jenseno-avtemporal-attention'
    camcan_dir = '/Volumes/quinna-camcan/dataman/data_information'


# Specify specific file names
mTBI_root = op.join(rds_dir, 'Projects/mTBI-predict')
bids_root = op.join(mTBI_root, 'collected-data', 'BIDS', 'task_BIDS')  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, 
                     suffix=meg_suffix, extension=meg_extension)
deriv_folder = op.join(bids_root, 'derivatives', 'sub-' + subject, 
                       'task-' + task)  # RDS folder for results
bids_fname = bids_path.basename.replace(meg_suffix, input_suffix)  # only used for suffices that are not recognizable to bids 
input_fname = op.join(deriv_folder, bids_fname)
deriv_fname = str(input_fname).replace(input_suffix, deriv_suffix)

# Read max filtered data 
raw_sss = mne.io.read_raw_fif(input_fname, preload=True)  # read_raw_bids doesn't work on derivatives

# Identifying and annotating eye blinks using vEOG (EOG001)
raw_sss.copy().pick_channels(ch_names=['EOG001','EOG002'   # vEOG, hEOG, EKG
                                       ,'ECG003']).plot()  # 'plot to make sure channel' 
                                                           # 'names are correct, rename otherwise'
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
raw_sss.set_channel_types({'EOG001':'eog', 'EOG002':'eog', 'ECG003':'ecg'})  # set both vEOG and hEOG as EOG channels
eog_picks = mne.pick_types(raw_sss.info, meg=False, eog=True)
scale = dict(eog=500e-6)
raw_sss.plot(order=eog_picks, scalings=scale, start=50)

# Save the artifact annotated file
raw_sss.save(deriv_fname, overwrite=True)













