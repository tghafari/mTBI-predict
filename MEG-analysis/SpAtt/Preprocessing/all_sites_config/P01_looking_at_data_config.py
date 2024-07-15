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

from config import session_info

# Specify specific file names
bids_path = BIDSPath(subject=session_info.subject, 
                     session=session_info.session, 
                     task=session_info.task, 
                     run=session_info.run, 
                     datatype=session_info.datatype,
                     suffix=session_info.meg_suffix, 
                     extension=session_info.extension,
                     root=session_info.bids_root)

# read and print raw data + meta information
raw = read_raw_bids(bids_path=bids_path, 
                    verbose=False,
                    extra_params={'preload':True})

# Plot PSD on raw data up to 60Hz
raw.compute_psd(fmax=60).plot()
mne.viz.plot_raw_psd(raw, fmin=.5, fmax=40, n_fft=None, picks=None)

# Plot 10 first seconds of raw data
raw.copy().crop(tmax=180).pick(["meg", "stim"]).filter(l_freq=0.1, h_freq=80).plot(title="raw")  # should be filtered bcz of cHPI high freq noise



print("Reporting output of P01_looking_at_data_config")
html_report_fname = op.join(session_info.report_folder, 
                            f'report_{session_info.subject}_{session_info.session}_{session_info.task}_raw_psd.html')
report_html = mne.Report(title=f'sub-{session_info.subject}_{session_info.task}')

raw.pick(["meg", "stim", "eog", "ecg"]).filter(l_freq=0.1, h_freq=80).load_data()
report_html.add_raw(raw=raw, 
               title='Raw', 
               psd=True, 
               tags=('raw')) 
report_html.save(html_report_fname, 
            overwrite=True, 
            open_browser=True)  # to check how the report looks

full_report_input = input("Do you want to add this to the full report now? (y/n)")
if full_report_input == 'y':
    raw_report_fname = op.join(session_info.report_folder,
                           f'report_sub-{session_info.subject}_{session_info.session}_{session_info.task}_raw.hdf5')
 
    report = mne.Report(title=f'sub-{session_info.subject}_{session_info.task}_raw')
    raw.pick(["meg", "stim", "eog", "ecg"]).filter(l_freq=0.1, h_freq=80).load_data()
    report.add_raw(raw=raw, 
                   title='Raw', 
                   psd=True, 
                   tags=('raw')) 
    report.save(raw_report_fname, 
                overwrite=True)
