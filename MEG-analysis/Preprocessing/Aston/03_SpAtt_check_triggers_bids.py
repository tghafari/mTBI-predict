#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 10:23:46 2024

@author: waitta
"""
import os.path as op
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mne
from mne_bids import BIDSPath, read_raw_bids

# fill these out

subject = '2011'  # subject code in mTBI project
session = '01A'  # data collection session within each run
run = '01'  # data collection run for each participant
meg_suffix = 'meg'
meg_extension = '.fif'
events_suffix = 'events'
events_extension = '.tsv'


######################## Spatial Attention #########################
# start with spatial attention
task = 'SpAtt' 

# specify specific file names
bids_root = r'/clinical/vol113/raw-sub-data/BIDS/task_BIDS'  #folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, datatype ='meg',
                     suffix=meg_suffix, extension=meg_extension)

# read and plot raw stim channel
# raw = read_raw_bids(bids_path=bids_path, verbose=False, 
#                     extra_params={'preload':True, 'allow_maxshield':'yes'})
# n_active = mne.chpi.get_active_chpi(raw)
# print(f"Average number of coils active during recording: {n_active.mean()}")


raw = read_raw_bids(bids_path=bids_path, verbose=False, 
                     extra_params={'preload':True})
raw.copy().crop(tmax=25.0).pick("meg").filter(l_freq=0.1, h_freq=150).plot()

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
durations_onset = ['cue', 'catch', 'stim', 'dot', 'response_press']
durations_offset = ['cue'] #, 'stim', 'dot']  # stim and dot are removed in actual data collection
direction_onset = ['cue_onset', 'dot_onset']
events_dict = {}

for dur in durations_onset:    
    events_dict[dur + "_onset"] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'{dur}_onset'),
                                               'onset'].to_numpy()
for dur in durations_offset:   
    events_dict[dur + "_offset"] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'{dur}_offset'),
                                               'onset'].to_numpy()
for dirs in direction_onset:
    events_dict[dirs + "_right"] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'{dirs}_right'),
                                               'onset'].to_numpy()
    events_dict[dirs + "_left"] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'{dirs}_left'),
                                               'onset'].to_numpy()

# compare number of trials with stimuli and responses
numbers_dict = {}
for numbers in  ['cue_onset_right', 'cue_onset_left', 'dot_onset_right', 'dot_onset_left', 
                      'response_press_onset']:
    numbers_dict[numbers] = events_dict[numbers].size
    
fig, ax = plt.subplots()
bars = ax.bar(range(len(numbers_dict)), list(numbers_dict.values()))
plt.xticks(range(len(numbers_dict)), list(numbers_dict.keys()), rotation=45)
ax.bar_label(bars)
plt.show()

# Check duration of cue presentation  
events_dict['cue_duration'] = events_dict['cue_offset'] - events_dict['cue_onset']
events_dict['stim_to_dot_duration'] = events_dict['dot_onset'] - events_dict['stim_onset']

#AW Had to add try except loop as more response presses recorded vs dot onset
try:    
    events_dict['RT'] = events_dict['response_press_onset'] - events_dict['dot_onset']
except: 
    #r_counter = 0
    AllRTs = []
    trials = events_dict['dot_onset']
    buttonpress = events_dict['response_press_onset']
    for i in range(0, len(trials)): #range(len(trials)):#in trials:
        if i == 0:
            r_counter = -1
            if trials[i]<buttonpress[r_counter+1]:
                r_counter = r_counter+1
                iRT = buttonpress[r_counter]-trials[i]
                AllRTs.append(iRT)
            elif trials[i]>buttonpress[r_counter+1]:
                r_counter = r_counter+2
                iRT = buttonpress[r_counter]-trials[i]
                AllRTs.append(iRT)
        elif i>0:            
            if trials[i]<buttonpress[r_counter+1]:
                r_counter = r_counter+1
                iRT = buttonpress[r_counter]-trials[i]
                AllRTs.append(iRT)
            elif trials[i]>buttonpress[r_counter+1]:
                r_counter = r_counter+2
                iRT = buttonpress[r_counter]-trials[i]
                AllRTs.append(iRT)
        
    events_dict['RT'] = AllRTs          

# Plot all durations
#fig, ax = plt.subplots()
for dur in ['cue_duration', 'stim_to_dot_duration', 'RT']:
    fig, ax = plt.subplots()
    plt.hist(events_dict[dur])
    plt.title(dur)
    plt.xlabel('time in sec')
    plt.ylabel('number of events')
    plt.show()
    