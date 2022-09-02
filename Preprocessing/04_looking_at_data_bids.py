# -*- coding: utf-8 -*-
"""
===============================================
04. Looking at the data

this code reads data in bids format and displays
information and raw data

written by Tara Ghafari
adapted from flux pipeline
==============================================
"""

import os.path as op

from mne_bids import BIDSPath, read_raw_bids

# fill these out
site = 'Birmingham'
subject = '03'  # subject code in mTBI project
session = '01'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'P' # is the data collected 'P'ilot or 'T'ask?
task = 'SpAtt'


# specify specific file names
bids_root = r'Z:\MEG_data\MNE-bids-data'  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root)
bids_fname = op.join('sub-' + subject + '_ses-' + session + '_task-' + task + 
                     '_run-' + run)  # type of data should be added to the end of this name

# read and print raw data + meta information
raw = read_raw_bids(bids_path=bids_path, verbose=False)
print(raw)
print(raw.info)

# Plot PSD on raw data up to 60Hz
raw.plot_psd(fmax=60)

# Plot 10 first seconds of raw data
raw.plot(duration=10, title='raw')
