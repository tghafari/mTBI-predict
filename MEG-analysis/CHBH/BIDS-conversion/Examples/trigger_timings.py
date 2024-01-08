# -*- coding: utf-8 -*-
"""
Checking the trigger timings for equipment testing

Script by Tara Ghafari
"""

import os
import mne

""" reading in data """

data_path = r'Z:\MEG_data\no_name\220421'
file_name = ['trigger_test_210422.fif']
path_data = os.path.join(data_path, file_name[0])

trigger_data = mne.io.read_raw_fif(path_data)

print(trigger_data)
print(trigger_data.info)

"""
Converting a STIM channel signal to an Event array:
The sample number of the onset (or offset) of each pulse is recorded as the event time, 
the pulse magnitudes are converted into integers.
"""
# Plotting raw STIM channels
trigger_data.copy().pick_types(meg=False, stim=True).plot(start=3, duration=6)  

# Convert events into array
events_onset = mne.find_events(trigger_data, stim_channel='STI101', min_duration=0.005)  # onset of triggers
events_offset = mne.find_events(trigger_data, stim_channel='STI101', output='offset', min_duration=0.005)  # offset of triggers

# N. of samples between onset and offset of events
cue_dur = events_onset[events_onset[:,2] == 4, 0] - events_onset[events_onset[:,2] == 2, 0]  # should be 200ms
stim_dur = events_onset[events_onset[:,2] == 128, 0] - events_onset[events_onset[:,2] == 8, 0]  # should be 1.5-3 sec
dot_dur = events_offset [events_offset[:,2] == 16, 0] - events_onset[events_onset[:,2] == 16, 0]  # should be 100ms