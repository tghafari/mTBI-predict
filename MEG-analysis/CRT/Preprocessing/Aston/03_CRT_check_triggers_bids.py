#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 10:25:24 2024

@author: waitta
"""
#%%
import os.path as op
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import mne
from mne_bids import BIDSPath, read_raw_bids

# fill these out

subject = '2001'  # subject code in mTBI project
session = '04A'  # data collection session within each run
run = '01'  # data collection run for each participant
meg_suffix = 'meg'
meg_extension = '.fif'
events_suffix = 'events'
events_extension = '.tsv'

platform = 'laptop' #'bluebear' # are you using 'bluebear', 'windows' or 'laptop'?

#%%
###################################### Choice Reaction Task ##########################################                                       
task = 'CRT' 

# Specify specific file names
if platform == 'bluebear':
    rds_dir = r'/rds/projects/s/sidhuc-mtbi-data' #r'\\its-rds.bham.ac.uk\rdsprojects\s\sidhuc-mtbi-data' #'/rds/projects/j/jenseno-avtemporal-attention'
    data_root = op.join(rds_dir, r'Alice_Aston_testing')
    #mTBI_root = op.join(rds_dir, r'Projects/mTBI-predict')
    #data_root = op.join(mTBI_root, 'collected-data')
elif platform == 'laptop':
    rds_dir = r'C:\Users\waitta\Documents\ClusterDocs'
    data_root = op.join(rds_dir, 'BearTestSub')

# Specify specific file names
bids_root = op.join(data_root, 'BIDS', 'task_BIDS')  # RDS folder for bids formatted data
#bids_root = r'/clinical/vol113/raw-sub-data/BIDS/task_BIDS'  #folder for bids formatted data

bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, datatype ='meg',
                     suffix=meg_suffix, extension=meg_extension)

raw = read_raw_bids(bids_path=bids_path, verbose=False)
raw.copy().pick_types(meg=False, stim=True).plot()

#%%
# Passing the TSV file to read_csv() with tab separator
events_bids_path = bids_path.copy().update(suffix=events_suffix,
                                           extension=events_extension)
events_file = pd.read_csv(events_bids_path, sep='\t')
event_onsets = events_file[['onset', 'value', 'trial_type']]

# Plot all events
event_onsets.plot(kind='scatter', x='onset', y='trial_type')
plt.xlabel('onset(sec)')
plt.ylabel('event type')
plt.show()

# Check durations using triggers
durations_onset = ['cue', 'trial', 'response'] 
direction_onset = ['cue_onset', 'response_onset']

events_dict = {}

for dur in durations_onset:    
    events_dict[dur + "_onset"] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'{dur}_onset'),
                                               'onset'].to_numpy()
for dirs in direction_onset:
    events_dict[dirs + "_right"] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'{dirs}_right'),
                                               'onset'].to_numpy()
    events_dict[dirs + "_left"] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'{dirs}_left'),
                                               'onset'].to_numpy()

# compare number of trials with stimuli and responses
numbers_dict = {}
for numbers in  ['cue_onset_right', 'cue_onset_left', 'response_onset_right', 'response_onset_left']:
    numbers_dict[numbers] = events_dict[numbers].size
    
fig, ax = plt.subplots()
bars = ax.bar(range(len(numbers_dict)), list(numbers_dict.values()))
plt.xticks(range(len(numbers_dict)), list(numbers_dict.keys()), rotation=45)
ax.bar_label(bars)
plt.show()

#%%
# Check duration of cue presentation  
# AW Had to add try except loop as not enough trial onset triggers recorded
try:
    events_dict['cue_to_dot_duration'] = events_dict['cue_onset'] - events_dict['trial_onset'] #erroring as not enough trial_onset recorded
    events_dict['RT'] = events_dict['response_onset'] - events_dict['cue_onset'] 

    for dur in ['cue_to_dot_duration', 'RT']:
        fig, ax = plt.subplots()
        plt.hist(events_dict[dur])
        plt.title(dur)
        plt.xlabel('time in sec')
        plt.ylabel('number of events')
        plt.show()       

except:
    print('Could not work out cue to dot duration as trigger mismatch')
    print('Number of cue_onset triggers')
    print(len(events_dict['cue_onset']))
    print('Number of trial_onset triggers')
    print(len(events_dict['trial_onset']))
    
    events_dict['RT'] = events_dict['response_onset'] - events_dict['cue_onset'] 

    for dur in ['RT']:
        fig, ax = plt.subplots()
        plt.hist(events_dict[dur])
        plt.title(dur)
        plt.xlabel('time in sec')
        plt.ylabel('number of events')
        plt.show()
        
#Get actual RTs from .mat file as Aston button triggers not correct
#beh_data_root = r'/clinical/vol113/raw-sub-data'
#Beh_data_folder = op.join(beh_data_root, 'sub_' + subject, 'ses_' + session, 'Behaviour')  # RDS folder for MEG data
#file_extension = '.mat'
#file_name = op.join('sub-' + subject + '_ses-' + session + '_task-' + task + '_run-' + run + '_logfile')
#raw_fname = op.join(Beh_data_folder, file_name + file_extension)

#need to read in matlab file using something like this
# import scipy.io        
# mat = scipy.io.loadmat(raw_fname)       
# %%
