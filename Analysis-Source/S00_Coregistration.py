# -*- coding: utf-8 -*-
"""
===============================================
S00. Coregistration and preparing trans file

This script coregisteres the MEG file with MRI
and generates the trans file (which is necessary
                              for BIDS conversion)
Run recon_all on freesurfer before this script.
The coregistration process is automatic.


written by Tara Ghafari
adapted from Oscar Ferrante
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
from mne_bids import BIDSPath, write_raw_bids, read_raw_bids


# subject info 
site = 'Birmingham'
subject = '04'  # subject code in mTBI project
session = '01'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'P' # is the data collected 'P'ilot or 'T'ask?
task = 'SpAtt'
meg_extension = '.fif'
meg_suffix = 'meg'
deriv_suffix = 'coreg'
mr_sub = f'sub-{subject}'

# Specify specific file names
bids_root = r'Z:\Projects\mTBI_predict\Collected_Data\MNE-bids-data' #'-anonymized'  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, 
                     suffix=meg_suffix, extension=meg_extension)
deriv_folder = op.join(bids_root, 'derivatives', 'flux-pipeline',
                       'sub-' + subject, 'task-' + task)  # RDS folder for results
deriv_root = bids_path.basename.replace(meg_suffix, deriv_suffix)  # only used for suffices that are not recognizable to bids 
deriv_fname = op.join(deriv_folder, deriv_root)

mr_sub_dir = r'Z:\Projects\mTBI_predict\Collected_Data\MRI_data\sub-04'
mr_figname = op.join(mr_sub_dir, 'fs_parsed.png')

# Step 1: reconstruct the MRI file using freesurfer 
""" use bluebear to reconstruct the MRI with my_recon.sh
     and visualise"""
Brain = mne.viz.get_brain_class()
brain = Brain(mr_sub, hemi='lh', surf='pial',
              subject_dir=mr_sub_dir, size=(800,600))
brain.save_image(mr_figname)

# Step 2: reconstruct the scalp surface with mne




info = read_raw_bids(bids_path=bids_path, verbose=False).info
# plot_kwargs = dict(subject=subject, subject_dir=bids_path.directory)
fiducials = "estimated"  # gets fiducials from fsaverage
coreg = mne.coreg.Coregistration(info, subject='sub-04', 
                                 subjects_dir=op.join(bids_path.directory, 'mri'),
                                 fiducials=fiducials)
Brain = mne.viz.get_brain_class()
brain = Brain(subject='sub-04', 
              hemi='lh', surf='pial',
              subjects_dir=op.join(bids_path.directory, 'mri'),
              size=(800,600))
brain.add_annotation('aparc', borders=False)
mne.gui.coregistration(subject='sub-04', subjects_dir=op.join(bids_path.directory, 'mri'))


# just trying mne example
data_path = mne.datasets.sample.data_path()
subject_dir = data_path / 'subjects'
subject = 'sample'

fname_raw = data_path / 'MEG' / subject / f'{subject}_audvis_raw.fif'
info = mne.io.read_info(fname_raw)
