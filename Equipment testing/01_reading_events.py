"""
===============================================
02. Extract events from the stimulus channels

this code is used to check and plot the timings
of triggers and creates -event.fif file

written by Tara Ghafari
adapted from Oscar Ferrante 
==============================================
ToDos:
1)    add if nottingham use ...
    else use ...
"""

# Import relevant Python modules
import os.path as op
import os

import mne
import matplotlib.pyplot as plt

# fill these out
site = 'Nottingham'
subject = '02'
session = '01'
task = 'SpAtt'
run = '01'
day = '14'  # date of data collection -> removed after anonymization
month = '07'
year = '2022'
pilot = 'P' # is the data collected 'P'ilot or 'T'ask?

# only usefule if you want to take the name of task and everything from file name
# if 'SaApp'.upper().lower() in file_name:
#     task = 'SpAtt'
# elif 'CRT'.upper().lower() in file_name:
#     task = 'CRT'
# elif 'EmoFace'.upper().lower() in file_name:
#     task = 'EmoFace'
 
# specify specific file names
if site == 'Aston' or site == 'Birmingham':
    data_path = r'Z:\MEG_data\Equipment testing-raw\dong_wer\220615'
    file_extension = '.fif'
    file_name = op.join(pilot + '1' + subject + '_' + task + '_' + day + month +
                        year + '_meg')
elif site == 'Nottingham':
    data_path = r'Z:\MEG_data\Equipment testing-raw\NottinghamEquipTest'
    file_prename = 'phantom_mTBIPredict_'
    file_extension = '.ds'
    file_name = op.join(file_prename + year + month + day + '_' + task.lower() 
                        + 'trigcheck')
    
# Read the events from stim channel
raw_fname = os.path.join(data_path, file_name + file_extension) 

# read raw and define the stim channel
if 'fif' in file_extension:
    raw = mne.io.read_raw_fif(raw_fname,allow_maxshield=True,verbose=True,preload=True)
    stim_channel = 'STI101'

elif 'ds' in file_extension:
    raw = mne.io.read_raw_ctf(raw_fname,system_clock='truncate',verbose=True,preload=True)
    stim_channel = 'UPPT002'
    

events = mne.find_events(raw, stim_channel=stim_channel,min_duration=0.001001,
                         consecutive=False, mask=65280,
                         mask_type='not_and')  #' mask removes triggers associated
                                               # with response box channel 
                                               # (not the response triggers)'

# Save the events in a dedicted FIF-file: 
filename_events = op.join(data_path,file_name + '-eve' + file_extension)
mne.write_events(filename_events, events, overwrite=True)

# Visualise a part of the events-array
plt.stem(events[:,0], events[:,2])
plt.xlim(min(events[:,0]), max(events[:,0]))
plt.xlabel('sample')
plt.ylabel('Trigger value (UPPT002)')
plt.show()





