# -*- coding: utf-8 -*-
"""
===============================================
P06. Annotation of artifacts

This code will identify artifacts and then annotate
them for later use (eg., to reject).

written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:
    1) consider using auto_rejection for
    blink threshold

Issues:
    1) for 200705B had to manually change thresh=3e-4 + ECG is 04, vEOG is 02
    2) no vEOG for 201005B

Contributions to community:
    1) read-Raw-bids doesn't work on the derivatives
    folder -> using mne_io_read_raw_fif instead
    2) BIDSPath doesn't read sss as suffix
    
Questions:
    1) why blink_onsets has -0.25?

"""

import os.path as op
import numpy as np
import matplotlib.pyplot as plt

import mne
from mne.preprocessing import annotate_muscle_zscore
from mne_bids import BIDSPath

from config import Config

# Initialize the config
config = Config()

# fill these out
input_suffix = 'raw_sss'
deriv_suffix = 'ann'
test_plot = True  # set to True if you want to plot the data for testing

bids_path = BIDSPath(subject=Config.subject, 
                     session=Config.session, 
                     task=Config.task, 
                     run=Config.run, 
                     root=Config.bids_root)

bids_fname = bids_path.basename.replace(Config.meg_suffix, input_suffix)  
input_fname = op.join(Config.deriv_folder, bids_fname)
deriv_fname = str(input_fname).replace(input_suffix, deriv_suffix)

# Read max filtered data 
raw_sss = mne.io.read_raw_fif(input_fname, preload=True)  # read_raw_bids doesn't work on derivatives

# Identifying and annotating eye blinks using vEOG (EOG001)
""" vEOG, hEOG, EKG: plot to make sure channel names are correct, rename otherwise'"""
raw_sss.copy().pick_channels(ch_names=['EOG001','EOG002','ECG003']).plot()  
raw_sss.set_channel_types({'EOG001':'eog', 'EOG002':'eog', 'ECG003':'ecg'})  # set both vEOG and hEOG as EOG channels

# Blinks
print("detecting blinks")
blink_events = mne.preprocessing.find_eog_events(raw_sss, ch_name=['EOG001'])  # blinks
onset_blink = blink_events[:,0] / raw_sss.info['sfreq'] -.25 
onset_blink -= raw_sss.first_time  # first_time is  the time start time of the raw data
n_blinks = len(blink_events)  # length of the event file is the number of blinks in total
duration_blink = np.repeat(.5, n_blinks)  # 500ms duration for each blink
description_blink = ['blink'] * n_blinks
annotation_blink = mne.Annotations(onset_blink, duration_blink, description_blink)

# Saccades
print("detecting saccades")
saccade_events = mne.preprocessing.find_eog_events(raw_sss, ch_name=['EOG002'], thresh=4e-5)  # saccades
onset_saccade = saccade_events[:,0] / raw_sss.info['sfreq'] -.25 
onset_saccade -= raw_sss.first_time  
n_saccades = len(saccade_events)  
duration_saccade = np.repeat(.3, n_saccades)  # 300ms duration for each saccade
description_saccade = ['saccade'] * n_saccades
annotation_saccade = mne.Annotations(onset_saccade, duration_saccade, description_saccade)

# Muscle artifacts
""" 
muscle artifacts are identified from the magnetometer data filtered and 
z-scored in filter_freq range
"""
annotation_muscle, scores_muscle = annotate_muscle_zscore(raw_sss, 
                                                          ch_type='mag', 
                                                          threshold=Config.threshold_muscle, 
                                                          min_length_good=Config.min_length_good, 
                                                          filter_freq=Config.filter_freq
                                                          )
# Plot muscle z-scores across recording
fig, ax = plt.subplots()
ax.plot(raw_sss.times, 
        scores_muscle)
ax.axhline(y=Config.threshold_muscle, color='r')
ax.set(xlabel='Time (s)', 
       ylabel='zscore', 
       title=f'Muscle activity (threshold = {Config.threshold_muscle})') 

annotation_muscle.onset -= raw_sss.first_time  # align the artifact onsets to data onset
annotation_muscle._orig_time = None  # remove date and time from the annotation variable

# Include annotations in dataset and inspect
raw_sss.set_annotations(annotation_blink + annotation_saccade + annotation_muscle)
eog_picks = mne.pick_types(raw_sss.info, 
                           meg=False, 
                           eog=True)
scale = dict(eog=500e-6)
raw_sss.plot(order=eog_picks, 
             scalings=scale, 
             start=50)

# Save the artifact annotated file
raw_sss.save(deriv_fname, 
             overwrite=True)













