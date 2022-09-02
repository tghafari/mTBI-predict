# -*- coding: utf-8 -*-
"""
===============================================
08. Epoching raw data based on conditions

This code will epoch continuous MEG signal based
on conditions saved in stim channel.

written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:
    1) read data from anonymized folder 
    
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

import mne


# fill these out
site = 'Birmingham'
subject = '03'  # subject code in mTBI project
session = '01'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'P' # is the data collected 'P'ilot or 'T'ask?
task = 'SpAtt'
file_extension = '.fif'
file_suffix = '-ica'

# Specify specific file names
bids_root = r'Z:\MEG_data\MNE-bids-data'  # RDS folder for bids formatted data
deriv_root = op.join(bids_root, 'derivatives', 'flux-pipeline' )  # RDS folder for results
deriv_folder = op.join(deriv_root , 'sub-' + subject, 'task-' + task)    
bids_fname = op.join('sub-' + subject + '_ses-' + session + '_task-' + task + 
                     '_run-' + run)  # define the ica cleaned file name
mne_read_raw_fname = op.join(deriv_folder, bids_fname + file_suffix + file_extension)

# read raw and events file
raw_ica = mne.io.read_raw_fif(mne_read_raw_fname, allow_maxshield=True,
                              verbose=True, preload=True)
events_file = pd.read_csv(op.join(bids_root, 'sub-' + subject, 'ses-' + session,
                                  'meg', bids_fname + '_events.tsv'), sep='\t')

# Some variable preparation in case we are using bids events file instead of mne
events = events_file[['sample','duration','value']].to_numpy().astype(int)
events[:,0] = events[:,0] + raw_ica.first_samp  # begin from the first sample
event_to_series = events_file.drop_duplicates(subset='trial_type')[['value','trial_type']]
event_id = pd.Series(event_to_series['value'].values, index=event_to_series['trial_type']).to_dict()
event_color = {'cue onset right':'red', 'cue onset left':'blue'}

# Take a quick look at the events file
plt.figure()
plt.stem(events_file['onset'], events_file['trial_type'])
plt.xlim(0,200)  # only show first 200 seconds
plt.xlabel('time (sec)')
plt.ylabel('event type')
plt.show()

# Set the peak-peak amplitude threshold for trial rejection.
""" subject to change based on data quality"""
reject = dict(grad=5000e-13,  # T/m (gradiometers)
              mag=5e-12,      # T (magnetometers)
              #eog=150e-6      # V (EOG channels)
              )

# Make epochs (2 seconds centered on stim onset)
epochs = mne.Epochs(raw_ica, events, event_id, tmin=-1.5, tmax=1,
                     baseline=None, proj=True, picks='all', detrend=1,
                     reject=reject, reject_by_annotation=True,
                     preload=True, verbose=True)
# Plotting
epochs.plot_drop_log()  # rejected epochs
epochs.plot(n_epochs=10, picks=['grad'], event_id={'cue onset right':101, 'dot onset right':211})
epochs.plot(n_epochs=1, picks=['stim'], event_id={'cue onset right':101})
epochs.plot(n_epochs=1, picks=['stim'], event_id={'cue onset left':102})
epochs['cue onset right','cue onset left'].plot(n_epochs=1, picks=['stim'], event_id=event_id,
                               event_color=event_color)
epochs['cue onset right'].filter(0.0,30).crop(-1.5,1).plot_image(
    picks=['MEG1732','MEG1742','MEG1932'],vmin=-100,vmax=100)  # event related field image



events_picks = events_file.loc[events_file['trial_type'].str.contains('cue onset','dot onset'),
                                           {'value','duration','sample'}].to_numpy()  # creates a variable like
                                                                                      # mne.pick_events
epochs['dot onset left'].plot(events=events_picks, event_id=event_id,
                               event_color=event_color, group_by='selection',
                               butterfly=True)  # see al sensors at once

# Save the epoched data
epochs.save(op.join(deriv_folder, bids_fname + '-epo' + 
                     file_extension), overwrite=True)


