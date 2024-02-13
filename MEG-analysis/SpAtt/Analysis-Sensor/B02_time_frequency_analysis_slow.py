# -*- coding: utf-8 -*-
"""
===============================================
B01. Time frequency representation of power (low freq)

This code will calculate TFR of powe for each 
trial and then averages over trials to characterize 
the modulation of oscillatory activity < 30Hz. 
Also, modulation index is calculated.

written by Tara Ghafari
adapted from flux pipeline
==============================================

"""

import os.path as op
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import mne
from mne_bids import BIDSPath

site = 'Birmingham'
subject = '2001'  # subject code in mTBI project
session = '02B'  # data collection session within each run
run = '01'  # data collection run for each participant
task = 'SpAtt'
meg_extension = '.fif'
meg_suffix = 'meg'
input_suffix = 'epo'
right_deriv_suffix = 'right-slow_tfr'
left_deriv_suffix = 'left-slow_tfr'

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
ROI_dir = op.join(mTBI_root, r'results-outputs/group-analysis/task-SpAtt/lateralisation-indices')
bids_root = op.join(mTBI_root, 'collected-data', 'BIDS', 'task_BIDS')  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, 
                     suffix=meg_suffix, extension=meg_extension)
deriv_folder = op.join(bids_root, 'derivatives', 'sub-' + subject, 
                       'task-' + task)  # RDS folder for results
bids_fname = bids_path.basename.replace(meg_suffix, input_suffix)  # only used for suffices that are not recognizable to bids 
input_fname = op.join(deriv_folder, bids_fname)
deriv_fname_right = str(input_fname).replace(input_suffix, right_deriv_suffix)
deriv_fname_left = str(input_fname).replace(input_suffix, left_deriv_suffix)

# Read ROI to show on topomap
ROI_fname = op.join(ROI_dir, f'sub-{subject}_ROI_1202.csv')
ROI_symmetric = pd.read_csv(ROI_fname)

# Read peak alpha freq and range
peak_alpha_fname = op.join(ROI_dir, f'sub-{subject}_peak_alpha.npz')  # 2 numpy arrays saved into an uncompressed file

# Read epoched data
epochs = mne.read_epochs(input_fname, verbose=True, preload=True)

# Set the parameters for slow freq analysis and run for attention left and right 
tfr_params = dict(picks=['grad','mag'], use_fft=True, return_itc=False, average=True, decim=2, n_jobs=4, verbose=True)

freqs = np.arange(2,31,1)  # the frequency range over which we perform the analysis
n_cycles = freqs / 2  # the length of sliding window in cycle units. 
time_bandwidth = 2.0  # '(2deltaTdeltaF) number of DPSS tapers to be used + 1.'
                      # 'it relates to the temporal (deltaT) and spectral (deltaF)' 
                      # 'smoothing'
                      # 'the more tapers, the more smooth'->useful for high freq data
                      
tfr_slow_right = mne.time_frequency.tfr_multitaper(epochs['cue_onset_right'],  
                                                  freqs=freqs, 
                                                  n_cycles=n_cycles,
                                                  time_bandwidth=time_bandwidth, 
                                                  **tfr_params                                                  
                                                  )                                                
tfr_slow_left = mne.time_frequency.tfr_multitaper(epochs['cue_onset_left'],  
                                                  freqs=freqs, 
                                                  n_cycles=n_cycles,
                                                  time_bandwidth=time_bandwidth, 
                                                  **tfr_params                                                  
                                                  )   
 
# Save the tfrs first
tfr_slow_right.save(deriv_fname_right, overwrite=True)
tfr_slow_left.save(deriv_fname_left, overwrite=True)

# Plot TFR on all sensors 
""" pick which sensors to show later""" 
tfr_slow_right.plot_topo(
    picks='grad',
    tmin=-.5, tmax=1.0, 
    baseline=[-.5,-.3],
    mode='percent',
    fig_facecolor='w', 
    font_color='k',
    vmin=-1, vmax=1,                      
    title='TFR of power (grad) < 30Hz - cue right')
tfr_slow_left.plot_topo(
    picks='grad',
    tmin=-.5, tmax=1.0,
    baseline=[-.5,-.3], 
    mode='percent',
    fig_facecolor='w', 
    font_color='k',
    vmin=-1, vmax=1, 
    title='TFR of power (grad) < 30Hz - cue left')

# Plot TFR for representative sensors - same in all participants
fig_tfr, axis = plt.subplots(2, 2, figsize = (7, 7))
sensors = ['MEG1733','MEG2133','MEG1943','MEG2533']

for idx, sensor in enumerate(sensors):
    if idx < len(sensors)/2:
        tfr_slow_left.plot(picks=sensor, baseline=[-.5,-.2],
                           mode='percent', tmin=-.5, tmax=1.0,
                           vmin=-.75, vmax=.75,
                           axes=axis[idx-2,1], show=False)
        axis[idx, 0].set_title(f'cue left-{sensor}')        
    else:   
        tfr_slow_right.plot(picks=sensor, baseline=[-.5,-.2],
                            mode='percent', tmin=-.5, tmax=1.0,
                            vmin=-.75, vmax=.75, 
                            axes=axis[idx-2,0], show=False)
        axis[idx-2, 1].set_title(f'cue right-{sensor}') 
        
axis[0, 0].set_ylabel('left sensors')  
axis[1, 0].set_ylabel('right sensors')  
axis[0, 0].set_xlabel('')  # Remove x-axis label for top plots
axis[0, 1].set_xlabel('')


fig_tfr.set_tight_layout(True)
plt.show()      
                      
# Plot post cue peak alpha range topographically
peak_alpha_file = np.load(peak_alpha_fname)
fmin_fmax_params = dict(fmin=peak_alpha_file['peak_alpha_freq_range'][0], fmax=peak_alpha_file['peak_alpha_freq_range'][-1])
fig_topo, axis = plt.subplots(1, 2, figsize=(7, 4))
tfr_slow_left.plot_topomap(tmin=.2, tmax=1.2, 
                           vlim=(-.5,.5),
                           baseline=(-.5, -.3), 
                           mode='percent', 
                           ch_type='grad',
                           **fmin_fmax_params,
                           axes=axis[0],
                           show=False)
tfr_slow_right.plot_topomap(tmin=.2, tmax=1.2, 
                            vlim=(-.5,.5),
                            baseline=(-.5, -.3), 
                            mode='percent',
                            ch_type='grad', 
                            **fmin_fmax_params,
                            axes=axis[1],
                            show=False)
axis[0].title.set_text('cue left')
axis[1].title.set_text('cue right')
fig_topo.suptitle("PAF range (grad), 0.35-0.75sec")
fig_topo.set_tight_layout(True)
plt.show()

# ================================== Calculate tfr for alpha for topoplots and MI ===========================================
tfr_alpha_params = dict(picks=['grad'], use_fft=True, return_itc=False, average=True, decim=2, n_jobs=4, verbose=True)

freqs = peak_alpha_file['peak_alpha_freq_range']  # peak frequency range loaded earlier
n_cycles = freqs / 2  # the length of sliding window in cycle units. 
time_bandwidth = 2.0 
                      
tfr_alpha_right = mne.time_frequency.tfr_multitaper(epochs['cue_onset_right'],  
                                                  freqs=freqs, 
                                                  n_cycles=n_cycles,
                                                  time_bandwidth=time_bandwidth, 
                                                  **tfr_alpha_params,
                                                  )  # shape: #sensors, #freqs, #time points                                   
tfr_alpha_left = mne.time_frequency.tfr_multitaper(epochs['cue_onset_left'],  
                                                  freqs=freqs, 
                                                  n_cycles=n_cycles,
                                                  time_bandwidth=time_bandwidth, 
                                                  **tfr_alpha_params,
                                                  )   
 
# Compare power modulation for attention right and left (always R- L)
tfr_alpha_modulation_power = tfr_alpha_left.copy()
tfr_alpha_modulation_power.data = (tfr_alpha_right.data - tfr_alpha_left.data) / (tfr_alpha_right.data + tfr_alpha_left.data)
sorted_test = tfr_alpha_modulation_power.data.sort()

tfr_alpha_modulation_power.plot_topo(tmin=-.5, tmax=1.2, 
                                     vmin=-.6, vmax=.6, 
                                     fig_facecolor='w', 
                                     font_color='k',
                                     title='attention right - attention left (PAF)')

# Plot mi on topoplot with highlighted ROI sensors
sensors = np.concatenate((ROI_symmetric['right_sensors'].values, 
                          ROI_symmetric['left_sensors'].values), axis=0)

fig, ax = plt.subplots()
fig_mi = tfr_alpha_modulation_power.plot_topomap(tmin=.2, tmax=1.2, 
                                                 **fmin_fmax_params, 
                                                 #vlim=(-.2,.2),
                                                 show=False, axes=ax)
# Plot markers for the sensors in ROI_right_sens
for sensor in sensors:
    ch_idx = tfr_alpha_modulation_power.info['ch_names'].index(sensor)
    x, y = tfr_alpha_modulation_power.info['chs'][ch_idx]['loc'][:2]
    ax.plot(x, y, 'ko', markerfacecolor='none', markersize=10)

fig_mi.suptitle('attention right - attention left (PAF range (grad))')
plt.show()                   

# Plot MI avg across ROI over time



# ===================================================================================================================

if summary_rprt:
   report_root = op.join(mTBI_root, r'results-outputs/mne-reports')  # RDS folder for reports
   report_folder = op.join(report_root , 'sub-' + subject, 'task-' + task)

   report_fname = op.join(report_folder, 
                          f'mneReport_sub-{subject}_{task}.hdf5')    # it is in .hdf5 for later adding images
   html_report_fname = op.join(report_folder, f'report_preproc_{task}.html')
   
   report = mne.open_report(report_fname)

   report.add_figure(fig=fig_tfr, title='TFR on ROI',
                     caption='Time Frequency Representation on \
                     right and left sensors', 
                     tags=('tfr'),
                     section='TFR'  # only in ver 1.1
                     )
   report.add_figure(fig=fig_topo, title='post stim alpha',
                     caption='post stim (0.35,0.75sec) alpha (8-12Hz)', 
                     tags=('tfr'),
                     section='TFR'
                     )         
   report.add_figure(fig=fig_mi, title='alpha modulation index on ROI',
                     caption='Alpha modulation index on ROI (att right - att left)- PAF (grad)', 
                     tags=('ali'),
                     section='ali'
                     )
   report.save(report_fname, overwrite=True)
   report.save(html_report_fname, overwrite=True, open_browser=True)  # to check how the report looks
