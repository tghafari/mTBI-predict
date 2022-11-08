# -*- coding: utf-8 -*-
"""
===============================================
08. Epoching raw data based on conditions

This code will epoch continuous MEG signal based
on conditions saved in stim channel and generates 
an HTML report about epochs.

written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:
    1) 
    
Issues/ contributions to community:
    1) events from bids needs preparation
    2) the labels and colors of events are not shown
    in epochs.plot (no difference with and 
                    withough event_color)
    
Questions:
    1) why isn't the trigger at the centre of each
    epoch?

"""

import os.path as op
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import mne
from mne_bids import BIDSPath

# fill these out
site = 'Birmingham'
subject = '04'  # subject code in mTBI project
session = '01'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'P' # is the data collected 'P'ilot or 'T'ask?
task = 'SpAtt'
meg_extension = '.fif'
meg_suffix = 'meg'
input_suffix = 'ica'
deriv_suffix = 'epo'

rprt = False

# Specify specific file names
bids_root = r'Z:\MEG_data\MNE-bids-data' #'-anonymized'  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, 
                     suffix=meg_suffix, extension=meg_extension)
deriv_folder = op.join(bids_root, 'derivatives', 'flux-pipeline' ,
                       'sub-' + subject, 'task-' + task)  # RDS folder for results
bids_fname = bids_path.basename.replace(meg_suffix, input_suffix)  # only used for suffices that are not recognizable to bids 
input_fname = op.join(deriv_folder, bids_fname)
deriv_fname = str(input_fname).replace(input_suffix, deriv_suffix)
event_fname = op.join(bids_path.directory, 'meg',
                      bids_path.basename.replace('meg.fif', 'events.tsv'))

rprt = False

# read raw and events file
raw_ica = mne.io.read_raw_fif(input_fname, allow_maxshield=True,
                              verbose=True, preload=True)
events_file = pd.read_csv(event_fname, sep='\t')

# Some variable preparation in case we are using bids events file instead of mne
events = events_file[['sample','duration','value']].to_numpy(dtype=int)
events[:,0] = events[:,0] + raw_ica.first_samp  # begin from the first sample
event_to_series = events_file.copy().drop_duplicates(subset='trial_type')[['value','trial_type']]
events_id = pd.Series(event_to_series['value'].values, index=event_to_series['trial_type']).to_dict()
events_color = {'cue onset right':'red', 'cue onset left':'blue'}

# creates a variable like mne.pick_events
events_picks = np.vstack(((events[events[:,2]==102]), (events[events[:,2]==101])))
events_picks[events_picks[:,0].argsort()]
events_picks_id = {k:v for k, v in events_id.items() if k.startswith('cue onset')}  # select only epochs you are interested in

# just for oscar's
# raw_list = list()
# events_list = list()
# events_list.append(events)
# raw_ica, events = mne.concatenate_raws(raw_list, preload=True,
#                                         events_list=events_list)
# end of oscar's

# Set the peak-peak amplitude threshold for trial rejection.
""" subject to change based on data quality"""
reject = dict(grad=5000e-13,  # T/m (gradiometers)
              mag=5e-12,      # T (magnetometers)
              #eog=150e-6      # V (EOG channels)
              )

# Make epochs (2 seconds centered on stim onset)
metadata, _, _ = mne.epochs.make_metadata(
                events=events, event_id=events_id, 
                tmin=-1.5, tmax=1, 
                sfreq=raw_ica.info['sfreq'])

epochs = mne.Epochs(raw_ica, events, events_id,   # select events_picks and events_picks_id                   
                    metadata=metadata,            # if only interested in specific events (not all)
                    tmin=-1.5, tmax=1,
                    baseline=None, proj=True, picks='all', 
                    detrend=1, event_repeated='drop',
                    reject=reject, reject_by_annotation=True,
                    preload=True, verbose=True)

# Take a quick look at the events file
plt.figure()
plt.stem(events_file['onset'], events_file['trial_type'])
plt.xlim(0,200)  # only show first 200 seconds
plt.xlabel('time (sec)')
plt.ylabel('event type')
plt.show()

# Plotting to check
epochs['cue onset left'].plot(events=events_picks, event_id=events_id,
                               event_color=events_color, group_by='selection',
                               butterfly=True)  # see al sensors at once

# Plots to save
fig_bads = epochs.plot_drop_log()  # rejected epochs
fig_right = epochs['cue onset right'].copy().filter(0.0,30).plot_image(
    picks=['MEG1932'],vmin=-100,vmax=100)  # event related field image
fig_left = epochs['cue onset left'].copy().filter(0.0,30).plot_image(
    picks=['MEG2333'],vmin=-100,vmax=100)  # event related field image

# Save the epoched data and generate report
epochs.save(deriv_fname, overwrite=True)
if rprt:
   report_root = r'Z:\Projects\mTBI predict\Results - Outputs\mne-Reports'  # RDS folder for results
   report_folder = op.join(report_root , 'sub-' + subject, 'task-' + task)
   report_fname = op.join(report_folder,
                          f'mneReport_sub-{subject}.hdf5')
   
   report = mne.open_report(report_fname)
   report.add_figure(fig=fig_bads, title='dropped epochs',
                     caption='number of dropped cue-centred epochs', 
                     tags=('bad-epoch-fig'),
                      section='epocheds'  # only in ver 1.1
                     )
   report.add_figure(fig=fig_right, title='cue right',
                     caption='evoked response on one left sensor (MEG1932)', 
                     tags=('right-epoch-fig'),
                      section='epocheds'
                     )
   report.add_figure(fig=fig_left, title='cue left',
                     caption='evoked response on one right sensor (MEG2333)', 
                     tags=('left-epoch-fig'),
                      section='epocheds' 
                     )   
   report.save(report_fname, overwrite=True, open_browser=True)
