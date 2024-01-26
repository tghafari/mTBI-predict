# -*- coding: utf-8 -*-
"""
Created on Thu Jul 28 12:52:55 2022

@author: ghafarit
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


# specify file names
data_path = r'Z:\MEG_data\Equipment testing-raw\NottinghamEquipTest'
file_prename = 'phantom_mTBIPredict_'
file_extension = '.ds'
file_name = op.join(file_prename + year + month + day + '_' + task.lower() 
                    + 'trigcheck')

# specify communal file names
raw_fname = op.join(data_path, file_name + file_extension)
events_data = op.join(data_path,file_name + '-eve' + file_extension)
output_path = r'Z:\MEG_data\MNE-pilot-data-bids'
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=output_path)

# read in raw file
raw = mne.io.read_raw_ctf(raw_fname,system_clock='truncate',verbose=True,preload=False)
stim_channel = 'UPPT002'

# Define events according to the event values 
block_num = {}
for num in range(1,3+1):
    block_num[f'block number {num:01d}'] = num + 10

other_events = {'cue onset right':101, 'cue onset left':102,
             'cue offset':103, 'catch trial':104, 'stim onset':201,
             'dot onset right':211, 'dot onset left':212,'response button press':255, 
             'block end':14,'experiment end':20, 'experiment abort':21}

events_id = block_num | other_events

# Write into BIDS format
write_raw_bids(raw, bids_path, events_data=events_data, 
               event_id=events_id, overwrite=True)