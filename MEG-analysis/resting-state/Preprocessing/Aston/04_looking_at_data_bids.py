# -*- coding: utf-8 -*-
"""
===============================================
04. Looking at the data

this code reads data in bids format and displays
information and raw data and generates an HTML
report

adapted by Alice Waitt for Aston
written by Tara Ghafari
adapted from flux pipeline
==============================================
"""

import os.path as op
import os
import pandas as pd
import mne
from mne_bids import BIDSPath, read_raw_bids

# fill these out
site = 'Aston'
subject = '2001'  # subject code in mTBI project
session = '04A'  # data collection session within each run
run = '01'  # data collection run for each participant
meg_suffix = 'meg'
task = 'rest'


rprt = True

# specify specific file names
data_root = r'/clinical/vol113/raw-sub-data/'
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

# AW Crop data file to start trigger +5 mins for rest.
if task == 'rest':
    events_suffix = 'events'
    events_extension = '.tsv'
    # Passing the TSV file to read_csv() with tab separator
    events_bids_path = bids_path.copy().update(suffix=events_suffix,
                                               extension=events_extension)
    events_file = pd.read_csv(events_bids_path, sep='\t')
    event_onsets = events_file[['onset', 'value', 'trial_type']]
    rest_st_time = event_onsets.loc[event_onsets['trial_type'].str.contains('rest_start'),
                                               'onset'].to_numpy()
    #t_min = np.round(rest_st_time, decimals=3)
    #t_max = np.round(rest_st_time+(60*5), decimals=3)
    t_min = rest_st_time
    t_max = rest_st_time+(60*5)
    raw.crop(tmin=float(t_min), tmax=float(t_max))
    
    deriv_root = op.join(bids_root, 'derivatives-test')  # RDS folder for results
    if not op.exists(op.join(deriv_root , 'sub-' + subject, 'ses-' + session, 'task-' + task, 'run-' + run)):
        os.makedirs(op.join(deriv_root , 'sub-' + subject, 'ses-' + session, 'task-' + task, 'run-' + run))
    deriv_folder = op.join(deriv_root , 'sub-' + subject, 'ses-' + session, 'task-' + task, 'run-' + run)
    deriv_suffix = 'crop_meg.fif'
    bids_fname = bids_path.basename.replace(meg_suffix, deriv_suffix)  # only used for suffices that are not recognizable to bids 
    deriv_fname = op.join(deriv_folder, bids_fname)
    raw.save(deriv_fname, overwrite=True)


# Plot 10 first seconds of raw data
#raw.copy().crop(tmax=180).pick(["meg", "stim"]).filter(l_freq=0.1, h_freq=150).plot(title="raw")  # should be filtered bcz of cHPI high freq noise
raw.copy().crop(tmax=180).pick(["meg", "stim"]).filter(l_freq=0.1, h_freq=80).plot(title="raw")  # should be filtered bcz of cHPI high freq noise
  

# picks = mne.pick_channels(raw.info["ch_names"], include=["MEG0931", "MEG1311", "MEG1331", "MEG1421", "MEG1431", "MEG2621", "MEG1441", "MEG1033", "MEG2513", "MEG2322", "MEG2033"])
# raw.plot(order=picks, n_channels=len(picks))

# raw.copy().crop(tmax=180).pick_channels(picks).filter(l_freq=0.1, h_freq=150).plot(title="raw")  # should be filtered bcz of cHPI high freq noise
# raw.copy().crop(tmax=180).filter(l_freq=0.1, h_freq=150).plot(order=picks, n_channels=len(picks),title="raw")  # should be filtered bcz of cHPI high freq noise
# raw.copy().pick_channels(ch_names=['EOG001','EOG002'   # vEOG, hEOG, EKG
#                                        ,'ECG003']).plot()

# Raw file report with all chanels
if rprt:
   report_root = r'/clinical/vol113/test-mne-reports'#mne-python-MEG-Reports'  # RDS folder for reports
   if not op.exists(op.join(report_root , 'sub-' + subject, 'ses-' +session, 'task-' + task, 'run-' + run)): #added ses
       os.makedirs(op.join(report_root , 'sub-' + subject, 'ses-' +session, 'task-' + task, 'run-' + run))
   report_folder = op.join(report_root , 'sub-' + subject, 'ses-' +session, 'task-' + task, 'run-' + run)
   report_fname = op.join(report_folder, 
                         f'mneReport_sub-{subject}_{task}_raw.hdf5')    # it is in .hdf5 for later adding images
   html_report_fname = op.join(report_folder, f'report_preproc_{task}_raw.html')
   # report_fname = op.join(report_folder, f'mneReport_sub-{subject}_ses-{session}.hdf5')    # it is in .hdf5 for later adding images
   # html_report_fname = op.join(report_folder, 'report_raw.html')
#report_fname = op.join(report_folder, 'report_raw.html')

#raw.pick(["meg", "stim", "eog", "ecg"]).filter(l_freq=0.1, h_freq=150).load_data()
raw.pick(["meg", "stim", "eog", "ecg"]).filter(l_freq=0.1, h_freq=80).load_data()

report = mne.Report(title=f'Subject n.{subject}')
#report = mne.Report(title='Raw data')
report.add_raw(raw=raw, title='Raw', psd=True,
               tags=('raw'))
report.save(report_fname, overwrite=True, open_browser=True)
report.save(html_report_fname, overwrite=True, open_browser=True)  # to check how the report looks