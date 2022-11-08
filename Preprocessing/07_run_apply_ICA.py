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
    1) read_raw_bids doesn't read annotated
    data
    
Questions:
    1) 

"""

import os.path as op

import mne
from mne.preprocessing import ICA
from mne_bids import BIDSPath

# fill these out
site = 'Birmingham'
subject = '04'  # subject code in mTBI project
session = '01'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'P' # is the data collected 'P'ilot or 'T'ask?
task = 'SpAtt'
meg_extension = '.fif'
meg_suffix = 'meg'
input_suffix = 'ann'
deriv_suffix = 'ica'

rprt = True

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

# read annotated data + resample and filtering
"""
we down sample the data in order to make ICA run faster, 
highpass filter at 1Hz to remove slow drifts and lowpass 40Hz
because that's what we need
"""
raw_ann = mne.io.read_raw_fif(input_fname, allow_maxshield=True,
                              verbose=True, preload=True)
raw_resmpld = raw_ann.copy().pick_types(meg=True)
raw_resmpld.resample(200)
raw_resmpld.filter(1, 40)

# raw_resmpld = mne.io.concatenate_raws([raw1_resmpld, raw2_resmpld])

# Apply ICA and identify artifact components
ica = ICA(method='fastica', random_state=97, n_components=30, verbose=True)
ica.fit(raw_resmpld, verbose=True)
ica.plot_sources(raw_resmpld, title='ICA')
ica.plot_components()

ICA_rej_dic = {'sub-03':[1,2,15],
               'sub-04':[0,7,28]}# manually selected bad ICs or from sub config file
artifact_ICs = ICA_rej_dic[f'sub-{subject}']


# Double check the manually selected artifactual ICs
""" Plot original data against reconstructed 
  signal excluding artifact ICs + Ic properties"""
  
ica.plot_overlay(raw_resmpld, exclude=[artifact_ICs[0]], picks='mag')  
ica.plot_overlay(raw_resmpld, exclude=[artifact_ICs[1]], picks='mag') 
ica.plot_overlay(raw_resmpld, exclude=[artifact_ICs[2]], picks='mag')  
ica.plot_overlay(raw_resmpld, exclude=artifact_ICs, picks='mag')  # all
ica.plot_properties(raw_resmpld, picks=artifact_ICs)

# Exclude ICA components
ica.exclude = artifact_ICs
raw_ica = raw_ann.copy()
ica.apply(raw_ica)

# raw_ica = mne.io.concatenate_raws([raw1_ica, raw2_ica])

# plot a few frontal channels before and after ICA
chs = ['MEG0311', 'MEG0121', 'MEG1211', 'MEG1411', 'MEG0342', 'MEG1432']
ch_idx = [raw_ann.ch_names.index(ch) for ch in chs]
raw_ann.plot(order=ch_idx, duration=5, title='before')
raw_ica.plot(order=ch_idx, duration=5, title='after')

# Save the ICA cleaned data
raw_ica.save(deriv_fname, overwrite=True)

# Filter data for the report
if rprt:
    report_root = r'Z:\Projects\mTBI predict\Results - Outputs\mne-Reports'  # RDS folder for results
    report_folder = op.join(report_root , 'sub-' + subject, 'task-' + task)
    report_fname = op.join(report_folder,
                       f'mneReport_sub-{subject}.hdf5')  
    
    report = mne.open_report(report_fname)
    report.add_ica(ica=ica, title='ICA cleaning', inst=None,
                   n_jobs=4, tags=('ica'))
    report.save(report_fname, overwrite=True)








