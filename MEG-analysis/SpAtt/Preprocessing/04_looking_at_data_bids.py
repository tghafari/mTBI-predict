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
subject = '2001'  # subject code in mTBI project
session = '02B'  # data collection session within each run
run = '01'  # data collection run for each participant
meg_suffix = 'meg'
task = 'rest'

rprt = True

# specify specific file names
data_root = r'Z:\Projects\mTBI-predict\collected-data'
bids_root = op.join(data_root, 'BIDS', 'task_BIDS')  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session, datatype ='meg',
                     suffix=meg_suffix, task=task, run=run, root=bids_root)

# read and print raw data + meta information
raw = read_raw_bids(bids_path=bids_path, verbose=False, 
                     extra_params={'preload':True})
print(raw)
print(raw.info)

# Plot PSD on raw data up to 60Hz
raw.compute_psd(fmax=60).plot()
mne.viz.plot_raw_psd(raw, fmin=.5, fmax=40, n_fft=None, picks=None)

# Plot 10 first seconds of raw data
raw.copy().crop(tmax=180).pick(["meg", "stim"]).filter(l_freq=0.1, h_freq=150).plot(title="raw")  # should be filtered bcz of cHPI high freq noise

# Raw file report with all chanels
if rprt:
    report_root = r'Z:\Projects\mTBI-predict\results-outputs\mne-reports'  # RDS folder for reports
    if not op.exists(op.join(report_root , 'sub-' + subject, 'task-' + task)):
        os.makedirs(op.join(report_root , 'sub-' + subject, 'task-' + task))
    report_folder = op.join(report_root , 'sub-' + subject, 'task-' + task)

    report_fname = op.join(report_folder, 'report_raw.html')
    raw.pick(["meg", "stim", "eog", "ecg"]).filter(l_freq=0.1, h_freq=150).load_data()
 
    report = mne.Report(title='Raw data')
    report.add_raw(raw=raw, title='Raw', psd=True)
    report.save(report_fname, overwrite=True, open_browser=True)
