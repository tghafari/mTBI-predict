#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 10:26:55 2024

@author: waitta
"""
import os.path as op
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mne
from mne_bids import BIDSPath, read_raw_bids

# fill these out

subject = '2002'  # subject code in mTBI project
session = '02A'  # data collection session within each run
run = '01'  # data collection run for each participant
meg_suffix = 'meg'
meg_extension = '.fif'
events_suffix = 'events'
events_extension = '.tsv'

###################################### Emotional face ##########################################
task = 'EmoFace' 

# specify specific file names
bids_root = r'/clinical/vol113/raw-sub-data/BIDS/task_BIDS'  #folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, datatype ='meg',
                     suffix=meg_suffix, extension=meg_extension)

raw = read_raw_bids(bids_path=bids_path, verbose=False)
raw.copy().pick_types(meg=False, stim=True).plot()

# Passing the TSV file to read_csv() with tab separator
events_bids_path = bids_path.copy().update(suffix=events_suffix,
                                           extension=events_extension)
events_file = pd.read_csv(events_bids_path, sep='\t')
event_onsets = events_file[['onset', 'value', 'trial_type']]

# # Plot all events
# event_onsets.plot(kind='scatter', x='onset', y='trial_type')
# plt.xlabel('onset(sec)')
# plt.ylabel('event type')
# plt.show()

# Display triggers separately in a scatter plot (scatter plot of all triggers is very busy)
triggers_to_show = event_onsets['trial_type'].str.contains('onset')                                         
event_onsets['trial_type']=='response female onset'  
event_onsets.loc[event_onsets['trial_type'].str.contains('response'),
                                            'onset'].to_numpy()
xData = event_onsets['onset']
yData = event_onsets['trial_type']
# Plot all events
fig, ax = plt.subplots() #AW Had to add in as didn't show fig before
plt.scatter(x=xData[triggers_to_show], y=yData[triggers_to_show])
plt.xlabel('onset(sec)')
plt.ylabel('event type')
plt.show()

# Check durations using triggers
face_onsets = ['happy','neutral','angry']
face_response = ['response_male','response_female']
face_gender = ['male', 'female']
onoffsets = ['trial_onset', 'question_onset','face_offset']

events_dict = {}

for emo in face_onsets:
    store = event_onsets.loc[event_onsets['trial_type'].str.contains(op.join('face_onset_'+emo)), #('face_onset_',f'{emo}'),
                                            'onset'].to_numpy()
    events_dict['face_' +emo] = store
    # events_dict["face_" + emo] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'{emo}'),
    #                                         'onset'].to_numpy()
for response in face_response:
    store = event_onsets.loc[event_onsets['trial_type'].str.contains(op.join(response+'_onset')),
                                            'onset'].to_numpy()
    events_dict['face_' +response] = store
    
for gender in face_gender:
    store = event_onsets.loc[event_onsets['trial_type'].str.contains(op.join('face_'+ gender)),
                                            'onset'].to_numpy()
    events_dict['face_' +gender] = store
    
for onoff in onoffsets:
    store = event_onsets.loc[event_onsets['trial_type'].str.contains(onoff),
                                            'onset'].to_numpy()
    events_dict[onoff] = store
#Orig check durations using triggesr   
# durations_onset = ['face', 'question', 'male'] # 'male' is included in both response female onset and response male onset
# durations_offset_sex = ['face'] 
# emotions = ['angry', 'neutral', 'happy']

# events_dict = {}

# for dur in durations_onset:    
#     events_dict[dur + "_onset"] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'{dur} onset'),
#                                                'onset'].to_numpy()
# for dur in durations_offset_sex:   
#     events_dict[dur + "_offset"] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'{dur} offset'),
#                                                'onset'].to_numpy()
# for sex in durations_offset_sex:
#     events_dict[sex + "_female"] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'{sex} female'),
#                                                'onset'].to_numpy()
#     events_dict[sex + "_male"] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'{sex} male'),
#                                                   'onset'].to_numpy()
# for emotion in emotions:
#     events_dict["face_" + emotion] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'face onset {emotion}'),
#                                                'onset'].to_numpy()       
                                          
# compare number of trials with stimuli and responses
numbers_dict = {}
# for numbers in  ['face_angry','face_happy','face_neutral','face_male','face_female',
#                  'question_onset','male_onset']:
#     numbers_dict[numbers] = events_dict[numbers].size
    
for trig in list(events_dict.keys()):
    numbers_dict[trig] = events_dict[trig].size
    
fig, ax = plt.subplots()
bars = ax.bar(range(len(numbers_dict)), list(numbers_dict.values()))
plt.xticks(range(len(numbers_dict)), list(numbers_dict.keys()), rotation=45)
ax.bar_label(bars)
plt.show()
     
# Check durations
#AW Had to add try except loop as some trial onsets missing
try:    
    events_dict['face_duration'] = events_dict['face_offset'] - events_dict['trial_onset']#['face_onset']
except: 
    AllTrls = []
    TrlsNoSt = [] # stored as if trial 1 = trial 0
    trial_st = events_dict['trial_onset']
    trial_end = events_dict['face_offset']
    for i in range(0, len(trial_st)): #range(len(trials)):#in trials:
        if i == 0:
            end_counter = 0
            if trial_st[i]<trial_end[end_counter]:
                iTrl = trial_end[end_counter]-trial_st[i]
                AllTrls.append(iTrl)
            elif trial_st[i]>trial_end[end_counter]:
                trlnum = end_counter+1
                TrlsNoSt.append(trlnum)
                #AllTrls.append(np.nan)
                end_counter = end_counter+1
                iTrl = trial_end[end_counter]-trial_st[i]
                AllTrls.append(iTrl)
            
        elif i>0:            
            if trial_st[i]<trial_end[end_counter+1]:
                end_counter = end_counter+1
                iTrl = trial_end[end_counter]-trial_st[i]
                AllTrls.append(iTrl)
            elif trial_st[i]>trial_end[end_counter+1]:
                while trial_st[i]>trial_end[end_counter+1]:
                    print('Trial missing start trigger:')
                    print(end_counter+1)
                    trlnum = end_counter+1
                    TrlsNoSt.append(trlnum)
                    #TrlsNoSt.append(end_counter+1)
                    #AllTrls.append(np.nan)
                    end_counter = end_counter+1                   
                else:
                    end_counter = end_counter+1
                    iTrl = trial_end[end_counter]-trial_st[i]
                    AllTrls.append(iTrl)
               
        
    events_dict['face_duration'] = AllTrls          


# remove extra fields for the longer array -- Ask Oscar's opinion
#events_dict['RT'] = events_dict['male_onset'] - events_dict['question_onset'] # male_onset is the response onset

female_response = events_dict['face_response_female']
male_response = events_dict['face_response_male']
all_responses = np.sort(np.concatenate((female_response,male_response)))

events_dict['button_press'] = all_responses
events_dict['RT'] = events_dict['button_press'] - events_dict['question_onset']
#events_dict['RT'] = events_dict['male_onset'] - events_dict['question_onset'] # male_onset is the response onset

# Plot durations
for dur in ['face_duration', 'RT']:
    plt.hist(events_dict[dur])
    plt.title(dur)
    plt.xlabel('time in sec')
    plt.ylabel('number of events')
    plt.show()
