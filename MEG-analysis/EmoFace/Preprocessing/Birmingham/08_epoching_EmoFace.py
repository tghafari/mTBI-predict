# -*- coding: utf-8 -*-
"""
===============================================
08. Epoching raw data based on conditions

This code will epoch continuous MEG signal based
on conditions saved in stim channel and generates 
an HTML report about epochs.

written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:
    1) which epochs to keep?
    
Issues/ contributions to community:

    
Questions:


"""

import os.path as op
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import mne
from mne_bids import BIDSPath, read_raw_bids

# fill these out
site = 'Birmingham'
subject = '2001'  # subject code in mTBI project
session = '02B'  # data collection session within each run
run = '01'  # data collection run for each participant
task = 'EmoFace'
meg_extension = '.fif'
meg_suffix = 'meg'
input_suffix = 'ica'
deriv_suffix = 'epo'

using_events_csv = False  # for when we are not using events_from_annotation. default is False
summary_rprt = True  # do you want to add evokeds figures to the summary report?
platform = 'mac'  # are you using 'bluebear', 'mac', or 'windows'?

if platform == 'bluebear':
    rds_dir = '/rds/projects/j/jenseno-avtemporal-attention'
    camcan_dir = '/rds/projects/q/quinna-camcan/dataman/data_information'
elif platform == 'windows':
    rds_dir = 'Z:'
    camcan_dir = 'X:/dataman/data_information'
elif platform == 'mac':
    rds_dir = '/Volumes/jenseno-avtemporal-attention'
    camcan_dir = '/Volumes/quinna-camcan/dataman/data_information'


# Specify specific file names
mTBI_root = op.join(rds_dir, r'Projects/mTBI-predict')
bids_root = op.join(mTBI_root, 'collected-data', 'BIDS', 'task_BIDS')  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, 
                     suffix=meg_suffix, extension=meg_extension)

raw = read_raw_bids(bids_path=bids_path, verbose=False, 
                     extra_params={'preload':True})  # read raw for events and event ids only

deriv_folder = op.join(bids_root, 'derivatives', 'sub-' + subject, 
                       'task-' + task)  # RDS folder for results
bids_fname = bids_path.basename.replace(meg_suffix, input_suffix)  # only used for suffices that are not recognizable to bids 
input_fname = op.join(deriv_folder, bids_fname)
deriv_fname = str(input_fname).replace(input_suffix, deriv_suffix)


# read raw and events file
raw_ica = mne.io.read_raw_fif(input_fname, allow_maxshield=True,
                              verbose=True, preload=True)
all_events, all_events_id = mne.events_from_annotations(raw, event_id='auto')

# Set the peak-peak amplitude threshold for trial rejection.
""" subject to change based on data quality"""
reject = dict(grad=5000e-13,  # T/m (gradiometers)
              mag=5e-12,      # T (magnetometers)
              #eog=150e-6      # V (EOG channels)
              )

# Make epochs (2 seconds centered on face offset): we are only epoching based on events we care about
event_ids_we_care_about = {'face_offset':116, "face_onset_angry":117, "face_onset_happy":118, 
                           "face_onset_neutral":119, "response_female_onset":121, "response_male_onset":122}

metadata, events, event_ids = mne.epochs.make_metadata(events=all_events, 
                                                event_id=event_ids_we_care_about, 
                                                tmin=-1.0, 
                                                tmax=1.0, 
                                                sfreq=raw_ica.info['sfreq'])

epochs = mne.Epochs(raw_ica, 
                events=events, 
                event_id=event_ids,                  
                metadata=metadata,  # if only interested in specific events (not all)
                tmin=-0.65,  # face duration=750-1000ms ISI duration=750-1000ms
                tmax=0.65,
                baseline=None, 
                proj=True, picks='all', 
                detrend=1, 
                event_repeated='drop',
                reject=reject, 
                reject_by_annotation=True,
                preload=True, 
                verbose=True)

# Which epochs were dropped?
fig_bads = epochs.plot_drop_log()  # rejected epochs

# Save the epoched data 
epochs.save(deriv_fname, overwrite=True)

############################### Check-up plots ################################
# Plotting to check the raw epoch
epochs['face_offset'].plot(events=events, event_id=event_ids, n_epochs=10)  # shows all the events in the epoched data that's based on 'cue_onset_left'

# plot amplitude on heads
times_to_topomap = [-.55, 0, .1, .55]
epochs['face_offset'].average(picks=['meg']).plot_topomap(times_to_topomap) 

# Topo plot evoked responses
evoked_obj_topo_plot = [epochs['face_offset'].average(picks=['grad'])]
mne.viz.plot_evoked_topo(evoked_obj_topo_plot, show=True)  # decide which sensors to show for the next section
epochs['face_offset'].copy().average(picks=['grad']).plot() 

############################# Plots to save #####################################
fig_right = epochs['face_offset'].copy().filter(0.0,30).plot_image(
    picks=['MEG2343'],vmin=-100,vmax=100)  # event related field image
fig_left = epochs['face_offset'].copy().filter(0.0,30).plot_image(
    picks=['MEG1923'],vmin=-100,vmax=100)  # event related field image

if summary_rprt:
    report_root = op.join(mTBI_root, r'results-outputs/mne-reports')  # RDS folder for reports
    
    if not op.exists(op.join(report_root , 'sub-' + subject, 'task-' + task)):
        os.makedirs(op.join(report_root , 'sub-' + subject, 'task-' + task))
    report_folder = op.join(report_root , 'sub-' + subject, 'task-' + task)

    report_fname = op.join(report_folder, 
        f'mneReport_sub-{subject}_{task}_1.hdf5')    # it is in .hdf5 for later adding images
    html_report_fname = op.join(report_folder, f'report_preproc_{task}_1.html')

    report = mne.open_report(report_fname)

    report.add_figure(fig=fig_right, title='face offset (0sec)',
                    caption='evoked response on one left sensor (MEG1923)', 
                    tags=('epo'),
                    section='epocheds'
                    )
    report.add_figure(fig=fig_left, title='face offset (0sec)',
                    caption='evoked response on one right sensor (MEG2343)', 
                    tags=('epo'),
                    section='epocheds' 
                    )   
    report.save(report_fname, overwrite=True, open_browser=True)
    report.save(html_report_fname, overwrite=True, open_browser=True)  # to check how the report looks
