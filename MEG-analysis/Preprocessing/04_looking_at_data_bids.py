# -*- coding: utf-8 -*-
"""
===============================================
04. Looking at the data

this code reads data in bids format and displays
information and raw data and generates an HTML
report

written by Tara Ghafari
adapted from flux pipeline
==============================================
"""

import os.path as op
import os

import mne
from mne_bids import BIDSPath, read_raw_bids

# fill these out
site = 'Birmingham'
subject = '2004'  # subject code in mTBI project
session = '01B'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'P' # is the data collected 'P'ilot or 'T'ask?
task = 'rest'

rprt = False

# specify specific file names
data_root = r'Z:\Projects\mTBI_predict\Collected_Data'
bids_root = op.join(data_root, 'BIDS')  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root)

# read and print raw data + meta information
raw = read_raw_bids(bids_path=bids_path, verbose=False)
print(raw)
print(raw.info)

# Plot PSD on raw data up to 60Hz
raw.compute_psd(fmax=60).plot()
mne.viz.plot_raw_psd(raw, fmin=.5, fmax=40, n_fft=None, picks=None)

# Plot 10 first seconds of raw data
raw.plot(duration=100, title='raw')

# Raw file report with all chanels
if rprt:
    report_root = r'Z:\Projects\mTBI predict\Results - Outputs\mne Reports'  # RDS folder for reports
    if not op.exists(op.join(report_root , 'sub-' + subject, 'task-' + task)):
        os.makedirs(op.join(report_root , 'sub-' + subject, 'task-' + task))
    report_folder = op.join(report_root , 'sub-' + subject, 'task-' + task)

    report_fname = op.join(report_folder, 'report_raw.html')
    
    raw.pick_types(meg=True, eog=True, ecg=True, stim=True).load_data()
 
    report = mne.Report(title='Raw data')
    report.add_raw(raw=raw, title='Raw', psd=True)
    report.save(report_fname, overwrite=True, open_browser=True)
