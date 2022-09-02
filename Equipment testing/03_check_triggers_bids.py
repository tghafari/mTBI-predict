# -*- coding: utf-8 -*-
"""
===============================================
03. Reads MEG data to checks triggers

this code uses reads meg events for equipment
testing

written by Tara Ghafari
==============================================
"""

import os.path as op
import pandas as pd
import matplotlib.pyplot as plt

import mne
from mne_bids import BIDSPath, read_raw_bids

# fill these out
site = 'Birmingham'
subject = '1'  # subject code in mTBI project
session = '01'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'P' # is the data collected 'P'ilot or 'T'ask?
task = 'SpAtt'


# specify specific file names
bids_root = r'Z:\MEG_data\MNE-bids-data-anonymized'  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root)
bids_fname = op.join('sub-' + subject + '_ses-' + session + '_task-' + task + 
                     '_run-' + run)  # type of data should be added to the end of this names

# read and plot raw stim channel
raw = read_raw_bids(bids_path=bids_path, verbose=False)
raw.copy().pick_types(meg=False, stim=True).plot()

# Passing the TSV file to read_csv() with tab separator
events_file = pd.read_csv(op.join(bids_root, 'sub-' + subject, 'ses-' + session,
                                  'meg', bids_fname + '_events.tsv'), sep='\t')
event_onsets = events_file[['onset', 'value', 'trial_type']]

# Check durations using triggers
durations = ['cue', 'stim', 'dot'] #, 'response'] # TODO only add after redoing bids with response onset - SpAtt
dur_dict = {}

for dur in durations:    
    dur_dict[dur + "_onset"] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'{dur} onset'),
                                               'onset'].to_numpy()
# Check duration of cue presentation
cue_offsets = event_onsets.loc[event_onsets['trial_type'].str.contains('cue offset'), 'onset']  # get the index of cue offset
cue_dur = cue_offsets.to_numpy() - dur_dict['cue_onset']

# Response duration # TODO only before redoing bids
response_onset = event_onsets.loc[event_onsets['trial_type'].str.contains('response'),
                                  'onset'].to_numpy()
RT = dur_dict['dot_onset'] - response_onset  # not enough responses
# Plot all cue durations
plt.hist(cue_dur)
event_onsets.plot(kind='scatter', x='onset', y='trial_type')
plt.show()


# Emotional Face -> not finalised:
#     dur_dict[dur + "_duration"] = dur_dict[dur + "_offset"] - dur_dict[dur + "_onset"]
    
# dur_dict["ISI_duration"] = dur_dict["face_onset"][1:] - dur_dict["face_offset"][:-1]
# dur_dict["RT"] = dur_dict["question_offset"] - event_onsets.loc\
#     [event_onsets['trial_type'].str.contains('response'), 'onset'].to_numpy() # doesn't work due to response triggers not being read in pilot data
    
conditions = ['angry', 'neutral', 'happy', 'male', 'female', 'onset', 'offset']  # for emoFace

for condition in conditions:
    dur_dict["face" + condition] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'face {condition}'), 
                                                   'onset'].to_numpy()
                                                   
dur_dict['question onset'] = event_onsets.loc[event_onsets['trial_type'].str.contains('question onset'), 
                                               'onset'].to_numpy()
dur_dict['response onset'] = event_onsets.loc[event_onsets['trial_type'].str.contains('responset'), 
                                               'onset'].to_numpy()
RT = dur_dict['response onset'] - dur_dict['question onset'][1:]

# older stuff- not finalised
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

# read events not using bids
events = mne.find_events(raw, stim_channel='STI101',min_duration=0.001001,
                          consecutive=False, mask=65280,
                          mask_type='not_and')  #' mask removes triggers associated
                                                # with response box channel 
                                                # (not the response triggers)'
events_qu_resp = mne.pick_events(events, include=[255, 102, 101])
