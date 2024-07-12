# -*- coding: utf-8 -*-
"""
===============================================
P01. Looking at the data

this code reads data in bids format and displays
information and raw data and generates an HTML
report. This is part of the automated preprocessing
pipeline.

written by Tara Ghafari
adapted from oscfer88
==============================================
"""

import os.path as op
import os

import mne
from mne_bids import BIDSPath, read_raw_bids

from config import session_info, directories


# Specify specific file names
bids_path = BIDSPath(subject=session_info.subject, 
                     session=session_info.session, 
                     task=session_info.task, 
                     run=session_info.run, 
                     datatype ='meg',
                     suffix='meg', 
                     root=directories.bids_root)

# read and print raw data + meta information
raw = read_raw_bids(bids_path=bids_path, 
                    verbose=False,
                    extra_params={'preload':True})

# Plot PSD on raw data up to 60Hz
raw.compute_psd(fmax=60).plot()
mne.viz.plot_raw_psd(raw, fmin=.5, fmax=40, n_fft=None, picks=None)

# Plot 10 first seconds of raw data
raw.copy().crop(tmax=180).pick(["meg", "stim"]).filter(l_freq=0.1, h_freq=80).plot(title="raw")  # should be filtered bcz of cHPI high freq noise

# Raw file report with all chanels
if summary_rprt:
    report_root = op.join(mTBI_root, 'results-outputs/mne-reports')  # RDS folder for reports
    if not op.exists(op.join(report_root , 'sub-' + subject, 'task-' + task)):
        os.makedirs(op.join(report_root , 'sub-' + subject, 'task-' + task))
    report_folder = op.join(report_root , 'sub-' + subject, 'task-' + task)
    report_fname = op.join(report_folder, 
                            f'mneReport_sub-{subject}_{task}_raw.hdf5')    # it is in .hdf5 for later adding images
    html_report_fname = op.join(report_folder, f'report_preproc_{task}_raw.html')

    raw.pick(["meg", "stim", "eog", "ecg"]).filter(l_freq=0.1, h_freq=80).load_data()

    report = mne.Report(title=f'sub-{subject}_{task}')
    report.add_raw(raw=raw, title='Raw', psd=True,
                   tags=('raw')) 
    report.save(report_fname, overwrite=True)
    report.save(html_report_fname, overwrite=True, open_browser=True)  # to check how the report looks
