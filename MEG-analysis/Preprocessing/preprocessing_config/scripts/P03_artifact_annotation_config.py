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
import sys
import argparse

import numpy as np
import matplotlib.pyplot as plt

import mne
from mne.preprocessing import annotate_muscle_zscore
from mne_bids import BIDSPath

# Add the project root directory to the sys.path
project_root = op.abspath(op.join(op.dirname(__file__), '..'))
config_root = op.join(project_root, 'config')
sys.path.append(config_root)

from config import Config

def read_and_prepare_raw(input_fname):
    print("Setting channel names")
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

def detect_and_annotate_muscle(raw, threshold_muscle, min_length_good, filter_freq):
    """ 
    muscle artifacts are identified from the magnetometer data filtered and 
    z-scored in filter_freq range
    """
    annotation_muscle, scores_muscle = annotate_muscle_zscore(raw, 
                                                              ch_type='mag', 
                                                              threshold=threshold_muscle, 
                                                              min_length_good=min_length_good, 
                                                              filter_freq=filter_freq)
    fig, ax = plt.subplots()
    ax.plot(raw.times, scores_muscle)
    ax.axhline(y=threshold_muscle, color='r')
    ax.set(xlabel='Time (s)', ylabel='zscore', title=f'Muscle activity (threshold = {threshold_muscle})')
    annotation_muscle.onset -= raw.first_time
    annotation_muscle._orig_time = None
    return annotation_muscle

def main(subject, session):
    # Initialize the config
    config = Config(site='Birmingham', subject=subject, session=session, task='SpAtt')

    eog_raw_plots = True  # Set to True if you want to plot annotated raw eog channels 

    _, input_fpath, deriv_fpath = config.directories.get_bids_paths(input_suffix='raw_sss', deriv_suffix='ann')

    raw_sss = read_and_prepare_raw(input_fpath)

    annotation_blink = detect_and_annotate_blinks(raw_sss)
    annotation_saccade = detect_and_annotate_saccades(raw_sss)
    annotation_muscle = detect_and_annotate_muscle(raw_sss, 
                                                   config.artifact_params.threshold_muscle,
                                                   config.artifact_params.min_length_good,
                                                   config.artifact_params.filter_freq)

    raw_sss.set_annotations(annotation_blink + annotation_saccade + annotation_muscle)

    if eog_raw_plots:

        eog_picks = mne.pick_types(raw_sss.info, meg=False, eog=True)
        scale = dict(eog=500e-6)
        raw_sss.plot(order=eog_picks, scalings=scale, start=50)

    raw_sss.save(deriv_fpath, overwrite=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Artifact Annotation")
    parser.add_argument('--subject', type=str, required=True, help='Subject ID')
    parser.add_argument('--session', type=str, required=True, help='Session ID')
    
    args = parser.parse_args()
    main(args.subject, args.session)