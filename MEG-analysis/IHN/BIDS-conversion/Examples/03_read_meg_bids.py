# -*- coding: utf-8 -*-
"""
===============================================
001. Reads MEG data to checks triggers

this code uses reads meg events for equipment
testing

written by Tara Ghafari
==============================================
"""

import os.path as op
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import mne
from mne_bids import BIDSPath, read_raw_bids

# Emotional Face
file_name = 'sub-01_ses-01_task-Emoface_run-01'
data_path = r'Z:\MEG_data\dong_wer\220615'

output_path = op.join(data_path, '..', 'MNE-pilot-data-bids')

bids_path = BIDSPath(subject='01', session='01',
                     task='EmoFace', run='01', root=output_path)

# Read raw stim channel
raw1 = read_raw_bids(bids_path=bids_path, verbose=False)

raw.copy().pick_types(meg=False, stim=True).plot()

events = mne.find_events(raw, stim_channel='UPPT002',min_duration=0.001001,
                          consecutive=False, mask=65280,
                          mask_type='not_and')  #' mask removes triggers associated
                                                # with response box channel 
                                                # (not the response triggers)'

events_qu_resp = mne.pick_events(events, include=[255, 254, 106])

# Passing the TSV file to read_csv() with tab separator
events_file = pd.read_csv(op.join(output_path, 'sub-01\ses-01\meg',
                                  file_name + '_events.tsv'), sep='\t')
event_onsets = events_file[['onset', 'value', 'trial_type']]

# Check durations using triggers
durations = ['face', 'question'] # ISI, RT, block
dur_dict = {}

for dur in durations:
    dur_dict[dur + "_onset"] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'{dur} on'), 'onset'].to_numpy()
    dur_dict[dur + "_offset"] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'{dur} off'), 'onset'].to_numpy()
    dur_dict[dur + "_duration"] = dur_dict[dur + "_offset"] - dur_dict[dur + "_onset"]
    
dur_dict["ISI_duration"] = dur_dict["face_onset"][1:] - dur_dict["face_offset"][:-1]
dur_dict["RT"] = dur_dict["question_offset"] - event_onsets.loc\
    [event_onsets['trial_type'].str.contains('response'), 'onset'].to_numpy() # doesn't work due to response triggers not being read in pilot data
dur_dict["block_duration"] =   
    
    
face_offsets = event_onsets.loc[event_onsets['trial_type'].str.contains('response'), 'onset']  # get the index of cue offset
face_onsets = event_onsets.loc[event_onsets['trial_type'].str.contains('question off'), 'onset']  # get the index of cue onset
face_dur = face_offsets.to_numpy() - face_onsets.to_numpy()

# Plot all cue durations
plt.hist(face_dur)
event_onsets.loc[event_onsets['trial_type'].isin(['face onset happy', 'face onset angry',
             'face onset neutral', 'face male', 'face female',
             'face offset', 'question on', 'question off',
             'response button male', 'response button female'])].plot(kind='scatter',
                                                                      x='onset', y='trial_type')
event_onsets.loc[event_onsets['trial_type'].isin(['question off',
             'response button male', 'response button female'])].plot(kind='scatter',
                                                                      x='onset', y='trial_type')
                                                                      
plt.show()

# Spatial Attention
file_name = 'sub-01_ses-01_task-SpAtt_run-01'
data_path = r'Z:\MEG_data\dong_wer\220615'

output_path = op.join(data_path, '..', 'MNE-pilot-data-bids')

bids_path = BIDSPath(subject='01', session='01',
                     task='SpAtt', run='01', root=output_path)

# Passing the TSV file to read_csv() with tab separator
events_file = pd.read_csv(op.join(output_path, 'sub-01\ses-01\meg',
                                  file_name + '_events.tsv'), sep='\t')
event_onsets = events_file[['onset', 'value', 'trial_type']]

# Check duration of cue presentation
dot_offsets = event_onsets.loc[event_onsets['trial_type'].str.contains('dot offset'), 'onset']  # get the index of cue offset
dot_onsets = event_onsets.loc[event_onsets['trial_type'].str.contains('dot onset'), 'onset']  # get the index of cue onset
dot_dur = dot_offsets.to_numpy() - dot_onsets.to_numpy()

# Plot all cue durations
plt.hist(dot_dur)
event_onsets.plot(kind='scatter', x='onset', y='trial_type')
plt.show()

# CRT

# Specify paths
file_name = 'sub-01_ses-01_task-CRT_run-01'
data_path = r'Z:\MEG_data\dong_wer\220615'

output_path = op.join(data_path, '..', 'MNE-pilot-data-bids')

bids_path = BIDSPath(subject='01', session='01',
                     task='CRT', run='01', root=output_path)

# Read the data and events
raw = read_raw_bids(bids_path=bids_path, verbose=False)

raw.copy().pick_types(meg=False, stim=True).plot()

events = mne.find_events(raw, stim_channel='STI101',min_duration=0.001001,
                          consecutive=False, mask=65280,
                          mask_type='not_and')  #' mask removes triggers associated
                                                # with response box channel 
                                                # (not the response triggers)'

events_qu_resp = mne.pick_events(events, include=[255, 254, 106])
raw.plot(events=events)

# Passing the TSV file to read_csv() with tab separator
events_file = pd.read_csv(op.join(output_path, 'sub-01\ses-01\meg',
                                  file_name + '_events.tsv'), sep='\t')
event_onsets = events_file[['onset', 'value', 'trial_type']]

# Check duration of cue presentation
cue_offsets = event_onsets.loc[event_onsets['trial_type'].str.contains('cue offset'), 'onset']  # get the index of cue offset
cue_onsets = event_onsets.loc[event_onsets['trial_type'].str.contains('cue onset'), 'onset']  # get the index of cue onset
cue_dur = cue_offsets.to_numpy() - cue_onsets.to_numpy()

# Plot all cue durations
plt.hist(cue_dur,range=[1.440,1.460])
event_onsets.plot(kind='scatter', x='onset', y='trial_type')
plt.show()

