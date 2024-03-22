# -*- coding: utf-8 -*-
"""
===============================================
A01. Event related fields

This code will generate ERFs in response to the
visual input.

written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:    
Questions:
    1) which conditions to equalize?

"""

import os.path as op
import os
import numpy as np

import mne
from mne_bids import BIDSPath

# fill these out
site = 'Birmingham'
subject = '2001'  # subject code in mTBI project
session = '02B'  # data collection session within each run
run = '01'  # data collection run for each participant
task = 'EmoFace'
meg_extension = '.fif'
meg_suffix = 'meg'
input_suffix = 'epo'
deriv_suffix = 'evo'

summary_rprt = True  # do you want to add evokeds figures to the summary report?
platform = 'mac'  # are you using 'bluebear', 'mac', or 'windows'?
test_plot = False  # do you want to plot the data to test (True) or just generate report (False)?

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
mTBI_root = op.join(rds_dir, 'Projects/mTBI-predict')
bids_root = op.join(mTBI_root, 'collected-data', 'BIDS', 'task_BIDS')  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, 
                     suffix=meg_suffix, extension=meg_extension)

deriv_folder = op.join(bids_root, 'derivatives', 'sub-' + subject, 
                       'task-' + task)  # RDS folder for results
bids_fname = bids_path.basename.replace(meg_suffix, input_suffix)  # only used for suffices that are not recognizable to bids 
input_fname = op.join(deriv_folder, bids_fname)
deriv_fname = str(input_fname).replace(input_suffix, deriv_suffix)

# Read epoched data
epochs = mne.read_epochs(input_fname, verbose=True, preload=True)

# Create a dictionary of epoch objects on face_onset_emotional vs face_onset_neutral
face_epochs = {}
face_epochs['face_emotional'] = epochs['event_name.str.endswith("y")'] 
face_epochs['face_neutral'] = epochs['face_onset_neutral']

# ==================================== Create evokeds for later and plots to save ==============================================
# Make evoked data for conditions of interest and save
evoked = epochs['face_onset_happy','face_onset_angry','face_onset_neutral'].copy().average(method='mean').filter(0.0,60)
mne.write_evokeds(deriv_fname, evoked, verbose=True, overwrite=True)

if test_plot:
    # Plot evoked data
    evoked.copy().apply_baseline(baseline=(-.3,0))
    evoked.copy().pick('mag').plot_topo(title='Magnetometers')
    evoked.copy().pick('mag').plot_topomap(.1, time_unit='s')

    evoked.copy().pick('grad').plot_topo(title='Gradiometers', merge_grads=True)
    evoked.copy().pick('grad').plot_topomap(.1, time_unit='s')

    # Explore the epoched dataset
    resampled_epochs = epochs.copy().resample(500)
    resampled_epochs.compute_psd().plot(spatial_colors=True)  # explore the frequency content of the epochs
    resampled_epochs.compute_psd().plot_topomap(ch_type='grad', 
                                    normalize=False)  # spatial distribution of the PSD

# Plot magnetometers for summary report
topos_times = np.arange(-50,450,30)*0.001
fig_mag = evoked.copy().pick('mag').plot_joint(times=topos_times, title='face onset 0s',
                                               topomap_args={'vlim':(-400,400)})

# Plot and combine gradiometers for summary report
fig_grad = evoked.copy().pick('grad').plot_joint(times=topos_times, title='face onset 0s',
                                                topomap_args={'vlim':(0,100)})

if summary_rprt:
    report_root = op.join(mTBI_root, 'results-outputs/mne-reports')  # RDS folder for reports
   
    if not op.exists(op.join(report_root , 'sub-' + subject, 'task-' + task)):
        os.makedirs(op.join(report_root , 'sub-' + subject, 'task-' + task))
    report_folder = op.join(report_root , 'sub-' + subject, 'task-' + task)

    report_fname = op.join(report_folder, 
                        f'mneReport_sub-{subject}_{task}_1.hdf5')    # it is in .hdf5 for later adding images
    html_report_fname = op.join(report_folder, f'report_preproc_{task}_1.html')
   
    report = mne.open_report(report_fname)
    report.add_figure(fig=fig_mag, title='evoked magnetometer',
                        caption='evoked response for face offset (face onset=-0.65s)', 
                        tags=('evo'),
                        section='evokeds'
                        )
    report.add_figure(fig=fig_grad, title='evoked gradiometer',
                        caption='evoked response for face offset (face onset=-0.65s)', 
                        tags=('evo'),
                        section='evokeds'
                        )
    report.save(report_fname, overwrite=True)
    report.save(html_report_fname, overwrite=True, open_browser=True)  # to check how the report looks
