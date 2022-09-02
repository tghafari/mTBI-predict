# -*- coding: utf-8 -*-
"""
===============================================
07. Run and apply ICA

This code will run ICA to find occular and cardiac
artifacts: 1. decomposition, 2. manual identification,
3. project out

written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:
    1) 
    2) 
    
Issues:
    1) 
    
Questions:
    1) 

"""

import os.path as op

import mne
from mne.preprocessing import ICA

# fill these out
site = 'Birmingham'
subject = '03'  # subject code in mTBI project
session = '01'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'P' # is the data collected 'P'ilot or 'T'ask?
task = 'SpAtt'
file_extension = '.fif'
file_suffix = '-sss-ann'


# Specify specific file names
bids_root = r'Z:\MEG_data\MNE-bids-data'  # RDS folder for bids formatted data
deriv_root = op.join(bids_root, 'derivatives', 'flux-pipeline' )  # RDS folder for results
deriv_folder = op.join(deriv_root , 'sub-' + subject, 'task-' + task)
bids_fname = op.join('sub-' + subject + '_ses-' + session + '_task-' + task + 
                     '_run-' + run)  # define the annotated file name
mne_read_raw_fname = op.join(deriv_folder, bids_fname + file_suffix + file_extension)

# read annotated data + resample and filtering
"""
we down sample the data in order to make ICA run faster, 
highpass filter at 1Hz to remove slow drifts and lowpass 40Hz
because that's what we need
"""

raw_ann = mne.io.read_raw_fif(mne_read_raw_fname, allow_maxshield=True,
                              verbose=True, preload=True)
raw_resmpld = raw_ann.copy().pick_types(meg=True)
raw_resmpld.resample(200)
raw_resmpld.filter(1, 40)

# Apply ICA and identify artifact components
ica = ICA(method='fastica', random_state=97, n_components=30, verbose=True)
ica.fit(raw_resmpld, verbose=True)
ica.plot_sources(raw_resmpld, title='ICA')
ica.plot_components()

artifact_ICs = [1,2,15]  # manually selected bad ICs

# Double check the manually selected artifactual ICs
""" Plot original data against reconstructed 
  signal excluding artifact ICs + Ic properties"""
  
ica.plot_overlay(raw_resmpld, exclude=[2], picks='mag')  # heart 
ica.plot_overlay(raw_resmpld, exclude=[15], picks='mag')  # blink
ica.plot_overlay(raw_resmpld, exclude=[1], picks='mag')  # eye

ica.plot_overlay(raw_resmpld, exclude=artifact_ICs, picks='mag')  # all
ica.plot_properties(raw_resmpld, picks=artifact_ICs)

# Exclude ICA components
ica.exclude = artifact_ICs
raw_ica = raw_ann.copy()
ica.apply(raw_ica)

# plot a few frontal channels before and after ICA
chs = ['MEG0311', 'MEG0121', 'MEG1211', 'MEG1411', 'MEG0342', 'MEG1432']
ch_idx = [raw_ann.ch_names.index(ch) for ch in chs]
raw_ann.plot(order=ch_idx, duration=5, title='before')
raw_ica.plot(order=ch_idx, duration=5, title='after')

# Save the ICA cleaned data
raw_ica.save(op.join(deriv_folder, bids_fname + '-ica' + 
                     file_extension), overwrite=True)













