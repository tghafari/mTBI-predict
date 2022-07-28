
"""
===============================================
01. Convert raw MEG data into BIDS format

this code converts raw MEG data (from .fif format)
to BIDS format

written by Tara Ghafari
adapted from Oscar Ferrante 
==============================================
"""

import os.path as op

import mne
from mne_bids import BIDSPath, write_raw_bids

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

# 'phantom_mTBIPredict_20220714_crttrigcheck2'
# 'P101_EmoFace_150622_meg'

# specify communal file names
raw_fname = op.join(data_path, file_name + file_extension)
events_data = op.join(data_path,file_name + '-eve' + file_extension)
output_path = r'Z:\MEG_data\MNE-pilot-data-bids'
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=output_path)

# Read in raw file
if 'fif' in file_extension:
    raw = mne.io.read_raw_fif(raw_fname,allow_maxshield=True,verbose=True,preload=False)
    stim_channel = 'STI101'

elif 'ds' in file_extension:
    raw = mne.io.read_raw_ctf(raw_fname,system_clock='truncate',verbose=True,preload=False)
    stim_channel = 'UPPT002'
    
    
# Define epochs according to the event values: 
if task == 'SpAtt':
    block_num = {}
    for num in range(1,3+1):
        block_num[f'block number {num:01d}'] = num + 10
    
    other_events = {'cue onset right':101, 'cue onset left':102,
                 'cue offset':103, 'catch trial':104, 'stim onset':201,
                 'dot onset right':211, 'dot onset left':212,'response button press':255, 
                 'block end':14,'experiment end':20, 'experiment abort':21}
    
    events_id = block_num | other_events
    
elif task == 'CRT':
    block_num = {}
    for num in range(1,3+1):
        block_num[f'block number {num:01d}'] = num + 10
        
    other_events = {'cue onset right':101, 'cue onset left':102,
                 'catch trial':104, 'response button right':254, 'response button left':255, 
                 'block end':14,'experiment end':20, 'experiment abort':21}
    
    events_id = block_num | other_events
    
elif task == 'EmoFace':
    face_id = {}
    stim_cat = ['face happy', 'face angry', 'face neutral']
    for count,stim in enumerate(stim_cat):
        for fid in range(35+1):  # range is an end half closed loop
            face_id[stim+f'_{1+fid:02d}'] = fid + 110 + count*40  # starting points are 110, 150, and 190
            
    block_num = {}
    for num in range(1,3+1):
        block_num[f'block number {num:01d}'] = num + 10
    
    other_events = {'face onset happy':101, 'face onset angry':102,
                 'face onset neutral':103, 'face male':231, 'face female':232,
                 'face offset':104, 'question onset':105,
                 'response button male':254, 'response button female':255, 
                 'block end':14,'experiment end':20, 'experiment abort':21}
    
    events_id = other_events | face_id | block_num

# Write into BIDS format
write_raw_bids(raw, bids_path, events_data=events_data, 
               event_id=events_id, overwrite=True)


