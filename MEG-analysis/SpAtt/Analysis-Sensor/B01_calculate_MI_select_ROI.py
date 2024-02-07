# -*- coding: utf-8 -*-
"""
===============================================
B02. calculate MI and select ROI

This code will 
    1. calculate TFR for cue right and left
    2. find peak alpha frequency in the averaged 
    power of all occipital gradiometers
    3. crop the time point and frequency (4-14Hz)
      of interest




    3. picks right sensors from the psd
    2. calculate (attend right - attend left) \
    / (attend right + attend left) 
    for right sensors
    3. sort sensors based on MI
    4. select first five sensors on right and their 
    corresponding left as ROI
    5. calculate MI for left corresponding sensros
    6. calculate HLM (MI on right sensors \
                      + MI on left corresponding sensors)
    7. report HLM and MI for ROI as primary outcomes



written by Tara Ghafari
==============================================
questions?


"""

import os.path as op
import numpy as np
import pandas as pd

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
deriv_suffix = 'psd'

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
deriv_fname = str(input_fname).replace(input_suffix, deriv_suffix)

ROI_fname = op.join(ROI_dir, f'sub-{subject}_ROI.csv')
MI_HLM_fname = op.join(ROI_dir, f'sub-{subject}_MI_HLM.csv')
ROI_MI_HLM_fname = op.join(ROI_dir, f'sub-{subject}_ROI_MI_HLM.csv')
ROI_MI_HLM_html =  op.join(ROI_dir, f'sub-{subject}_ROI_MI_HLM.html')

# Read sensor layout sheet from camcan RDS
sensors_layout_sheet = op.join(camcan_dir, 'sensors_layout_names.csv')
sensors_layout_names_df = pd.read_csv(sensors_layout_sheet)

# Remove the extra ' and " from the csv file
"""these variables are in correct right-and-left-corresponding-sensors order"""

right_sensors = sensors_layout_names_df['right_sensors'].to_list()
left_sensors = sensors_layout_names_df['left_sensors'].to_list()

# Read epoched data
epochs = mne.read_epochs(input_fname, verbose=True, preload=True)  # epochs are from -0.8 to 1.2

# ========================================= RIGHT SENSORS and ROI====================================
# Calculate tfr for post cue alpha
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

# Plot TFR on all sensors and check
""" pick which sensors to show later""" 
tfr_slow_right.plot_topo(tmin=-.5, tmax=1.0, 
                        baseline=[-.5,-.3], mode='percent',
                        fig_facecolor='w', font_color='k',
                        vmin=-1, vmax=1, 
                        title='TFR of power < 30Hz - cue right')
tfr_slow_left.plot_topo(tmin=-.5, tmax=1.0,
                         baseline=[-.5,-.3], mode='percent',
                         fig_facecolor='w', font_color='k',
                         vmin=-1, vmax=1, 
                         title='TFR of power < 30Hz - cue left')

## Finding peak alpha frequency
# Select occipital sensors
occipital_picks = mne.read_vectorview_selection("occipital")  # contains both mag and grad
occipital_picks =  [channel[-4:] for channel in occipital_picks]  # vectorview selection adds a space in the name of channels!

# Create a list of channel names from epochs.ch_names that have the same last four characters as occipital picks and pick only grads
occipital_channels = [channel for channel in epochs.pick('grad').ch_names if channel[-4:] in occipital_picks]

# Crop post stim alpha
tfr_slow_right_post_stim = tfr_slow_right.copy().crop(tmin=0.3,tmax=0.8,fmin=4, fmax=14).pick(occipital_channels)
tfr_slow_left_post_stim = tfr_slow_left.copy().crop(tmin=0.3,tmax=0.8,fmin=4, fmax=14).pick(occipital_channels)

# Find the frequency with the highest power for tfr_slow_right_post_stim
freq_idx_right = np.argmax(np.mean(np.abs(tfr_slow_right_post_stim.data), axis=0))
# Find the frequency with the highest power for tfr_slow_left_post_stim
freq_idx_left = np.argmax(np.mean(np.abs(tfr_slow_left_post_stim.data), axis=0))

# Get the corresponding frequencies
freq_right = tfr_slow_right_post_stim.freqs[freq_idx_right]
freq_left = tfr_slow_left_post_stim.freqs[freq_idx_left]







# Pick only right sensors for ROI-- the order of sensors is based on the list you input to pick from psd
right_psd = epochs['cue_onset_right'].copy().filter(0.1,60).compute_psd(**psd_params, n_jobs=4)
left_psd = epochs['cue_onset_left'].copy().filter(0.1,60).compute_psd(**psd_params, n_jobs=4)

# Get power and frequency data from right sensors
right_psds_right_sens, right_freqs_right_sens = right_psd.copy().pick(right_sensors).get_data(return_freqs=True)  # shape: #epochs, #sensors, #frequencies
left_psds_right_sens, left_freqs_right_sens = left_psd.copy().pick(right_sensors).get_data(return_freqs=True)

# Select alpha and average across epochs
alpha_l_freq, alpha_h_freq = 8, 13
right_alpha_psds_right_sens = right_psds_right_sens[:,:,(right_freqs_right_sens >= alpha_l_freq)
                                                    & (right_freqs_right_sens <= alpha_h_freq)]
right_alpha_psds_right_sens = np.mean(right_alpha_psds_right_sens, axis=(0,2))

left_alpha_psds_right_sens = left_psds_right_sens[:,:,(left_freqs_right_sens >= alpha_l_freq) 
                                                  & (left_freqs_right_sens <= alpha_h_freq)]
left_alpha_psds_right_sens = np.mean(left_alpha_psds_right_sens, axis=(0,2))

# Calculate MI for right sensors and sort
MI_right_sens = (right_alpha_psds_right_sens -left_alpha_psds_right_sens) \
              / (right_alpha_psds_right_sens + left_alpha_psds_right_sens)
MI_right_df = pd.DataFrame({'MI_right': MI_right_sens,
                            'right_sensors': right_sensors})  # cannot use right_sensors as the order is different

# ========================================= LEFT SENSORS =======================================
# Get power and frequency data from right sensors
right_psds_left_sens, right_freqs_left_sens = right_psd.copy().pick(left_sensors).get_data(return_freqs=True)  # shape: #epochs, #sensors, #frequencies
left_psds_left_sens, left_freqs_left_sens = left_psd.copy().pick(left_sensors).get_data(return_freqs=True)

# Select alpha and average across epochs
alpha_l_freq, alpha_h_freq = 8, 13
right_alpha_psds_left_sens = right_psds_left_sens[:,:,(right_freqs_left_sens >= alpha_l_freq)
                                                    & (right_freqs_left_sens <= alpha_h_freq)]
right_alpha_psds_left_sens = np.mean(right_alpha_psds_left_sens, axis=(0,2))

left_alpha_psds_left_sens = left_psds_left_sens[:,:,(left_freqs_left_sens >= alpha_l_freq) 
                                                  & (left_freqs_left_sens <= alpha_h_freq)]
left_alpha_psds_left_sens = np.mean(left_alpha_psds_left_sens, axis=(0,2))

# Calculate MI for right sensors and sort
MI_left_sens = (right_alpha_psds_left_sens -left_alpha_psds_left_sens) \
             / (right_alpha_psds_left_sens + left_alpha_psds_left_sens)
MI_left_df = pd.DataFrame({'MI_left': MI_left_sens,
                           'left_sensors': left_sensors})  # cannot use right_sensors as the order is different

# ========================================= ROI and HLM =======================================
# Sort the right MI DataFrame by MI value and extract the first 5 channel names and save the ROI sensors
df_sorted = MI_right_df.sort_values(by='MI', ascending=False)
ROI_right_sens = df_sorted["ch_names"].head(5).tolist()
MI_right_ROI = pd.DataFrame({'MI':df_sorted["MI"].head(5).tolist(),
                 'right_sensors': df_sorted["ch_names"].head(5).tolist()})  # create a df of MI right ROI sensors and their MI values

# Find the corresponding left sensors 
ROI_symmetric = sensors_layout_df_new[sensors_layout_df_new["right_sensors"].isin(ROI_right_sens)]
ROI_symmetric.to_csv(ROI_fname, index=False)

# Calculate HLM and put it with all MIs with right and left corresponding sensors in one df
HLM_all_sens = (MI_right_sens + MI_left_sens)
HLM_all_sens_df = pd.DataFrame({'HLM':HLM_all_sens})

MI_HLM_all_sens_df = pd.concat([MI_left_df, MI_right_df, HLM_all_sens_df], axis=1)  
MI_HLM_all_sens_df.to_csv(MI_HLM_fname, index=False)

ROI_HLM_df = MI_HLM_all_sens_df[MI_HLM_all_sens_df["right_sensors"].isin(ROI_right_sens)]
ROI_HLM_df.to_csv(ROI_MI_HLM_fname, index=False)

# Save and read the dataframe as html for the report
ROI_HLM_df.to_html(ROI_MI_HLM_html, index=False)
with open(ROI_MI_HLM_html, 'r') as f:
    html_string = f.read()

if summary_rprt:
   report_root = r'Z:\Projects\mTBI-predict\results-outputs\mne-reports'  # RDS folder for reports
   report_folder = op.join(report_root , 'sub-' + subject, 'task-' + task)

   report_fname = op.join(report_folder, 
                          f'mneReport_sub-{subject}_{task}.hdf5')    # it is in .hdf5 for later adding images
   html_report_fname = op.join(report_folder, f'report_preproc_{task}.html')
   
   report = mne.open_report(report_fname)

   report.add_html(html=html_string, 
                   section='HLM',  # only in ver 1.1
                   title='Primary Outcome',
                   tags=('hlm')
                    )
   report.save(report_fname, overwrite=True)
   report.save(html_report_fname, overwrite=True, open_browser=True)  # to check how the report looks





