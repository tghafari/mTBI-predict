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
subject = '2002'  # subject code in mTBI project
session = '04B'  # data collection session within each run
run = '01'  # data collection run for each participant
task = 'SpAtt'
meg_suffix = 'meg'

summary_rprt = True

platform = 'mac'  # are you using 'bluebear', 'mac', or 'windows'?

if platform == 'bluebear':
    rds_dir = '/rds/projects/j/jenseno-avtemporal-attention'
elif platform == 'windows':
    rds_dir = 'Z:'
elif platform == 'mac':
    rds_dir = '/Volumes/jenseno-avtemporal-attention'

# Specify specific file names
mTBI_root = op.join(rds_dir, 'Projects/mTBI-predict')
data_root = op.join(mTBI_root, 'collected-data')
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
