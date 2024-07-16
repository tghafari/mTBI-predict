# -*- coding: utf-8 -*-
"""
===============================================
P03. Annotation of artifacts

This code will identify artifacts and then annotate
them for later use (eg., to reject).

written by Tara Ghafari
adapted from flux pipeline
==============================================
Issues:
    1) for 200705B had to manually change thresh=3e-4 + ECG is 04, vEOG is 02
    2) no vEOG for 201005B
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

# Fill these out
input_suffix = 'raw_sss'
deriv_suffix = 'ann'
eog_raw_plots = True  # Set to True if you want to plot annotated raw eog channels 

bids_path = BIDSPath(subject=config.session_info.subject, 
                     session=config.session_info.session, 
                     task=config.session_info.task, 
                     run=config.session_info.run, 
                     root=config.directories.bids_root)

bids_fname = bids_path.basename.replace(config.session_info.meg_suffix, input_suffix)  
input_fname = op.join(config.directories.deriv_folder, bids_fname)
deriv_fname = input_fname.replace(input_suffix, deriv_suffix)

def read_and_prepare_raw(input_fname):
    raw = mne.io.read_raw_fif(input_fname, preload=True)
    raw.copy().pick_channels(['EOG001', 'EOG002', 'ECG003']).plot()
    raw.set_channel_types({'EOG001': 'eog', 'EOG002': 'eog', 'ECG003': 'ecg'})
    return raw

def detect_and_annotate_blinks(raw):
    print("Detecting blinks")
    blink_events = mne.preprocessing.find_eog_events(raw, ch_name='EOG001')
    onset_blink = blink_events[:, 0] / raw.info['sfreq'] - 0.25 - raw.first_time   # first_time is the time start time of the raw data
    n_blinks = len(blink_events)  # length of the event file is the number of blinks in total
    duration_blink = np.repeat(.5, n_blinks)  # 500ms duration for each blink
    description_blink = ['blink'] * n_blinks
    annotation_blink = mne.Annotations(onset_blink, duration_blink, description_blink)
    return annotation_blink

def detect_and_annotate_saccades(raw):
    print("Detecting saccades")
    saccade_events = mne.preprocessing.find_eog_events(raw, ch_name='EOG002', thresh=4e-5)
    onset_saccade = saccade_events[:, 0] / raw.info['sfreq'] - 0.25 - raw.first_time
    n_saccades = len(saccade_events)  
    duration_saccade = np.repeat(.3, n_saccades)  # 300ms duration for each saccade
    description_saccade = ['saccade'] * n_saccades
    annotation_saccade = mne.Annotations(onset_saccade, duration_saccade, description_saccade)
    return annotation_saccade

def detect_and_annotate_muscle(raw):
    """ 
    muscle artifacts are identified from the magnetometer data filtered and 
    z-scored in filter_freq range
    """
    annotation_muscle, scores_muscle = annotate_muscle_zscore(raw, 
                                                              ch_type='mag', 
                                                              threshold=config.artifact_params.threshold_muscle, 
                                                              min_length_good=config.artifact_params.min_length_good, 
                                                              filter_freq=config.artifact_params.filter_freq)
    fig, ax = plt.subplots()
    ax.plot(raw.times, scores_muscle)
    ax.axhline(y=config.artifact_params.threshold_muscle, color='r')
    ax.set(xlabel='Time (s)', ylabel='zscore', title=f'Muscle activity (threshold = {config.artifact_params.threshold_muscle})')
    annotation_muscle.onset -= raw.first_time
    annotation_muscle._orig_time = None
    return annotation_muscle

# Main function to handle all processing steps
def main():
    raw_sss = read_and_prepare_raw(input_fname)

    annotation_blink = detect_and_annotate_blinks(raw_sss)
    annotation_saccade = detect_and_annotate_saccades(raw_sss)
    annotation_muscle = detect_and_annotate_muscle(raw_sss)

    raw_sss.set_annotations(annotation_blink + annotation_saccade + annotation_muscle)

    if eog_raw_plots:

        eog_picks = mne.pick_types(raw_sss.info, meg=False, eog=True)
        scale = dict(eog=500e-6)
        raw_sss.plot(order=eog_picks, scalings=scale, start=50)

    raw_sss.save(deriv_fname, overwrite=True)

if __name__ == "__main__":
    main()
