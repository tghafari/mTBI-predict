# -*- coding: utf-8 -*-
"""
===============================================
03. Reads MEG data to checks triggers and raw
data

this code uses reads meg events for quality
testing

written by Tara Ghafari
==============================================
ToDos:
    1) rerun bids conversion 
Questions:
    1) why do we copy raw file?
    2) where is the copy() stored in variables?
    3) how come there are more gradio and magneto sensors after filtering?
"""

import os.path as op
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import mne
from mne_bids import BIDSPath, read_raw_bids

# fill these out

site = 'Birmingham'
subject = '2013'  # subject code in mTBI project
session = '01B'  # data collection session within each run
run = '01'  # data collection run for each participant
meg_suffix = 'meg'
meg_extension = '.fif'
events_suffix = 'events'
events_extension = '.tsv'

using_events_csv = True  # for when we are not using events_from_annotation. default is True because it's more intuitive to work with these tsv files 
                         # (as oppose to 08_epoching in which False is default) 

######################## Spatial Attention #########################
# start with spatial attention
task = 'SpAtt' 

# specify specific file names
bids_root = r'Z:\Projects\mTBI-predict\collected-data\BIDS\task_BIDS'  # RDS folder for bids formatted data
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

raw.copy().crop(tmax=180).pick(["meg", "stim"]).filter(l_freq=0.1, h_freq=150).plot()
raw.copy().pick(["stim"]).plot(duration=1.5)

if using_events_csv == False:
    events, events_id = mne.events_from_annotations(raw, event_id='auto')
        
elif using_events_csv:
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
    events_dict['RT'] = events_dict['response_press_onset'] - events_dict['dot_onset'] 
    # cheat line to add extra elements for easier calculation of RTs:
        #events_dict['dot_onset'] = np.insert(events_dict['dot_onset'], index_onset_should_be_added_before, onset)
    
    # Plot all durations
    for dur in ['cue_duration', 'stim_to_dot_duration', 'RT']:
        fig, ax = plt.subplots()
        plt.hist(events_dict[dur])
        plt.title(dur)
        plt.xlabel('time in sec')
        plt.ylabel('number of events')
        plt.show()
    
###################################### Choice Reaction Task ##########################################                                       
# update bids path and read raw data 
'remember to clear the variables before running this section'
'change response right/left onset to response onset right/left + add underscores'

bids_path.update(task='CRT')
raw = read_raw_bids(bids_path=bids_path, verbose=False,  
                    extra_params={'preload':True})  # preload needed for plotting

raw.copy().crop(tmax=180).pick(["meg", "stim"]).filter(l_freq=0.1, h_freq=150).plot()
raw.copy().pick(["stim"]).plot(duration=1.5)

if using_events_csv == False:
    events, events_id = mne.events_from_annotations(raw, event_id='auto')
        
elif using_events_csv:
    # Passing the TSV file to read_csv() with tab separator
    events_bids_path = bids_path.copy().update(suffix=events_suffix,
                                               extension=events_extension)
    events_file = pd.read_csv(events_bids_path, sep='\t')
    event_onsets = events_file[['onset', 'value', 'trial_type']]
    
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
    
    # Check duration of cue presentation  
    # events_dict['cue_to_dot_duration'] = events_dict['cue_onset'] - events_dict['trial_onset']  # doesn't work due to missed trial onset triggers (overlapping with reponse)
    events_dict['RT'] = events_dict['response_onset'] - events_dict['cue_onset'] 
        
    # Plot all durations
    for dur in ['RT']:
        fig, ax = plt.subplots()
        plt.hist(events_dict[dur])
        plt.title(dur)
        plt.xlabel('time in sec')
        plt.ylabel('number of events')
        plt.show()
    
###################################### Emotional face ##########################################

# update bids path and read raw data 
'remember to clear the variables before running this section'

bids_path.update(task='EmoFace')
raw = read_raw_bids(bids_path=bids_path, verbose=False)
raw.copy().pick_types(meg=False, stim=True).plot()

if using_events_csv == False:
    events, events_id = mne.events_from_annotations(raw, event_id='auto')
        
elif using_events_csv:
    # Passing the TSV file to read_csv() with tab separator
    events_bids_path = bids_path.copy().update(suffix=events_suffix,
                                               extension=events_extension)
    events_file = pd.read_csv(events_bids_path, sep='\t')
    event_onsets = events_file[['onset', 'value', 'trial_type']]
    
    # Display triggers separately in a scatter plot (scatter plot of all triggers is very busy)
    triggers_to_show = event_onsets['trial_type'].str.contains('onset')                                         
    event_onsets['trial_type']=='response female onset'  
    event_onsets.loc[event_onsets['trial_type'].str.contains('response'),
                                               'onset'].to_numpy()
    xData = event_onsets['onset']
    yData = event_onsets['trial_type']
    # Plot all events
    plt.scatter(x=xData[triggers_to_show], y=yData[triggers_to_show])
    plt.xlabel('onset(sec)')
    plt.ylabel('event type')
    plt.show()
    
    # Check durations using triggers
    durations_onset = ['face', 'question', 'male'] # 'male' is included in both response female onset and response male onset
    durations_offset_sex = ['face'] 
    emotions = ['angry', 'neutral', 'happy']
    
    events_dict = {}
    
    for dur in durations_onset:    
        events_dict[dur + "_onset"] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'{dur} onset'),
                                                   'onset'].to_numpy()
    for dur in durations_offset_sex:   
        events_dict[dur + "_offset"] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'{dur} offset'),
                                                   'onset'].to_numpy()
    for sex in durations_offset_sex:
        events_dict[sex + "_female"] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'{sex} female'),
                                                   'onset'].to_numpy()
        events_dict[sex + "_male"] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'{sex} male'),
                                                      'onset'].to_numpy()
    for emotion in emotions:
        events_dict["face_" + emotion] = event_onsets.loc[event_onsets['trial_type'].str.contains(f'face onset {emotion}'),
                                                   'onset'].to_numpy()       
                                              
    # compare number of trials with stimuli and responses
    numbers_dict = {}
    for numbers in  ['face_angry','face_happy','face_neutral','face_male','face_female',
                     'question_onset','male_onset']:
        numbers_dict[numbers] = events_dict[numbers].size
        
    fig, ax = plt.subplots()
    bars = ax.bar(range(len(numbers_dict)), list(numbers_dict.values()))
    plt.xticks(range(len(numbers_dict)), list(numbers_dict.keys()), rotation=45)
    ax.bar_label(bars)
    plt.show()
         
    # Check durations
    events_dict['face_duration'] = events_dict['face_offset'] - events_dict['face_onset']
    # remove extra fields for the longer array -- Ask Oscar's opinion
    events_dict['RT'] = events_dict['male_onset'] - events_dict['question_onset'] # male_onset is the response onset
    
    # Plot durations
    for dur in ['face_duration', 'RT']:
        plt.hist(events_dict[dur])
        plt.title(dur)
        plt.xlabel('time in sec')
        plt.ylabel('number of events')
        plt.show()