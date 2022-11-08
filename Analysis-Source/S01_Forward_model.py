# -*- coding: utf-8 -*-
"""
===============================================
S01. Constructing the forward model

This script constructs the head model to be used
as a lead field matrix, in source modelling. 
This is based on the T1 MRI. This model will 
be aligned to head position of the subject in the
MEG system. 

written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:
    1) 
    
Issues/ contributions to community:
    1) 
    
Questions:
    1)

"""
import numpy as np
import os.path as op
import matplotlib.pyplot as plt
from nilearn.plotting import plot_anat

import mne
from mne import head_to_mri
from mne_bids import BIDSPath, write_raw_bids, write_


# subject info 
site = 'Birmingham'
subject = '04'  # subject code in mTBI project
session = '01'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'P' # is the data collected 'P'ilot or 'T'ask?
task = 'SpAtt'
meg_extension = '.fif'
meg_suffix = 'meg'
input_suffix = 'epo'
deriv_suffix = 'svm'

rprt = False

# Specify specific file names
bids_root = r'Z:\MEG_data\MNE-bids-data' #'-anonymized'  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, 
                     suffix=meg_suffix, extension=meg_extension)
deriv_folder = op.join(bids_root, 'derivatives', 'flux-pipeline' ,
                       'sub-' + subject, 'task-' + task)  # RDS folder for results
bids_fname = bids_path.basename.replace(meg_suffix, input_suffix)  # only used for suffices that are not recognizable to bids 
input_fname = op.join(deriv_folder, bids_fname)
deriv_fname = str(input_fname).replace(input_suffix, deriv_suffix)