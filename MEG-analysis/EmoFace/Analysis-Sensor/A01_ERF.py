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
task = 'SpAtt'
meg_extension = '.fif'
meg_suffix = 'meg'
input_suffix = 'epo'
deriv_suffix = 'evo'

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

deriv_folder = op.join(bids_root, 'derivatives', 'sub-' + subject, 
                       'task-' + task)  # RDS folder for results
bids_fname = bids_path.basename.replace(meg_suffix, input_suffix)  # only used for suffices that are not recognizable to bids 
input_fname = op.join(deriv_folder, bids_fname)
deriv_fname = str(input_fname).replace(input_suffix, deriv_suffix)

# Read epoched data
epochs = mne.read_epochs(input_fname, verbose=True, preload=True)
conds_we_care_about = ["cue_onset_right", "cue_onset_left"]#, "stim_onset", "response_press_onset"] # TODO:discuss with Ole
epochs.equalize_event_counts(conds_we_care_about)  # this operates in-place

# ==================================== RIGHT LEFT SEPARATELY ==============================================
# Make evoked data for conditions of interest and save
evoked_right = epochs['cue_onset_right'].copy().average(method='mean').filter(0.0,50).crop(-.2,.8)  # the cues are fliped for P103
evoked_left = epochs['cue_onset_left'].copy().average(method='mean').filter(0.0,50).crop(-.2,.8)
evokeds = [evoked_right, evoked_left]

# Plot evoked data
epochs['cue_onset_right'].copy().filter(0.0,30).crop(-.2,.5).plot_image(picks=['MEG1932'],
                                                                        vmin=-200, vmax=200)
evoked_right.copy().apply_baseline(baseline=(-.2,0))
evoked_right.copy().pick('mag').plot_topo(title='Magnetometers')
evoked_right.copy().pick('mag').plot_topomap(.1, time_unit='s')

evoked_right.copy().pick('grad').plot_topo(title='Gradiometers',
                                                      merge_grads=True)
evoked_right.copy().pick('grad').plot_topomap(.1, time_unit='s')

# Explore the epoched dataset
resampled_epochs = epochs.copy().resample(200)
resampled_epochs.compute_psd(fmin=1.0, fmax=30.0).plot(spatial_colors=True)  # explore the frequency content of the epochs
resampled_epochs.compute_psd().plot_topomap(ch_type='grad', 
                                  normalize=False)  # spatial distribution of the PSD

# Plot magnetometers for summary report
fig_right_mag = evoked_right.copy().pick('mag').plot_joint(times=[0.150,0.270,0.410])
fig_left_mag = evoked_left.copy().pick('mag').plot_joint(times=[0.150,0.255,0.395])

# Plot and combine gradiometers for summary report
fig_right_grad = evoked_right.copy().pick('grad').plot_joint(
    times=[0.150,0.270,0.410], 
    topomap_args={'vlim':(0,140)})
fig_left_grad = evoked_left.copy().pick('grad').plot_joint(
    times=[0.150,0.255,0.395],
    topomap_args={'vlim':(0,140)})

## Generate report for evoked separately
#html_report_evkd_fname = op.join(report_folder, f'report_preproc_{task}-evokeds.html')

#report = mne.Report(title='Evoked data')
#report.add_evokeds(evokeds=evokeds, 
#                   titles=['cue right',
#                           'cue left'],
#                   n_time_points=10)
#ßreport.save(html_report_evkd_fname, overwrite=True, open_browser=True)  # to check how the report looks

# ==================================== RIGHT LEFT TOGETHER ==============================================
# Make evoked data for conditions of interest and save
evoked = epochs['cue_onset_right','cue_onset_left'].copy().average(
                                                    method='mean').filter(0.0,60).crop(-.2,.8)  
mne.write_evokeds(deriv_fname, evoked, verbose=True)

# Plot evoked data
evoked.copy().apply_baseline(baseline=(-.2,0))
evoked.copy().pick('mag').plot_topo(title='Magnetometers')
evoked.copy().pick('mag').plot_topomap(.1, time_unit='s')

evoked.copy().pick('grad').plot_topo(title='Gradiometers', merge_grads=True)
evoked.copy().pick('grad').plot_topomap(.1, time_unit='s')

# Explore the epoched dataset
resampled_epochs = epochs.copy().resample(200)
resampled_epochs.compute_psd(fmin=1.0, fmax=30.0).plot(spatial_colors=True)  # explore the frequency content of the epochs
resampled_epochs.compute_psd().plot_topomap(ch_type='grad', 
                                  normalize=False)  # spatial distribution of the PSD

# Plot magnetometers for summary report
topos_times = np.arange(50,450,30)*0.001
fig_mag = evoked.copy().pick('mag').plot_joint(times=topos_times)

# Plot and combine gradiometers for summary report
fig_grad = evoked.copy().pick('grad').plot_joint(times=topos_times, 
                                                topomap_args={'vlim':(0,140)})

if summary_rprt:
    report_root = op.join(mTBI_root, r'results-outputs/mne-reports')  # RDS folder for reports
   
    if not op.exists(op.join(report_root , 'sub-' + subject, 'task-' + task)):
        os.makedirs(op.join(report_root , 'sub-' + subject, 'task-' + task))
    report_folder = op.join(report_root , 'sub-' + subject, 'task-' + task)

    report_fname = op.join(report_folder, 
                        f'mneReport_sub-{subject}_{task}_2.hdf5')    # it is in .hdf5 for later adding images
    html_report_fname = op.join(report_folder, f'report_preproc_{task}_2.html')
   
    report = mne.open_report(report_fname)
    report.add_figure(fig=fig_mag, title='evoked magnetometer',
                        caption='evoked response for cue = 0-200ms', 
                        tags=('evo'),
                        section='evokeds'
                        )
    report.add_figure(fig=fig_grad, title='evoked gradiometer',
                        caption='evoked response for cue = 0-200ms', 
                        tags=('evo'),
                        section='evokeds'
                        )
    report.save(report_fname, overwrite=True)
    report.save(html_report_fname, overwrite=True, open_browser=True)  # to check how the report looks

