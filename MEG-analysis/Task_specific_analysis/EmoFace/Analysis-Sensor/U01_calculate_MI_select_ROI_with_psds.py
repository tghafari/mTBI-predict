# -*- coding: utf-8 -*-
"""
===============================================
B02. calculate MI and select ROI

This code will:

    A. Peak Alpha Frequency
    1. calculate TFR for cue right and left
    2. crop the tfr into time point and frequency (4-14Hz)
      of interest and pick occipital sensors
    3. find peak alpha frequency range and plot

    B. ROI sensors
    4. calculate psd for right sensors 
    5. calculate MI = (attend right - attend left) \
    / (attend right + attend left) 
    6. sort sensors based on MI
    7. select first five sensors on right and their 
    corresponding left as ROI
    8. calculate psd for left sensors and MI_left_sens
    9. calculate ALI = MI_right_ROI_avg +
                       MI_left_ROI_avg
    10. report ALI as primary outcome


written by Tara Ghafari
==============================================
questions?


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

ROI_fname = op.join(ROI_dir, f'sub-{subject}_ROI_1202.csv')
MI_ALI_fname = op.join(ROI_dir, f'sub-{subject}_MI_ALI.csv')
ROI_MI_ALI_fname = op.join(ROI_dir, f'sub-{subject}_ROI_MI_ALI.csv')
ROI_MI_ALI_html =  op.join(ROI_dir, f'sub-{subject}_ROI_MI_ALI.html')

peak_alpha_fname = op.join(ROI_dir, f'sub-{subject}_peak_alpha.npz')  # 2 numpy arrays saved into an uncompressed file
# Read sensor layout sheet from camcan RDS
"""these variables are in correct right-and-left-corresponding-sensors order"""
sensors_layout_sheet = op.join(camcan_dir, 'sensor_layout_name_grad_no_central.csv')
sensors_layout_names_df = pd.read_csv(sensors_layout_sheet)

right_sensors = [ch[1:8] for ch in sensors_layout_names_df['right_sensors']]
left_sensors = [ch[1:8] for ch in sensors_layout_names_df['left_sensors']]
sensors_layout_df = pd.DataFrame({'left_sensors': left_sensors,
                                  'right_sensors': right_sensors})  

# Read epoched data
epochs = mne.read_epochs(input_fname, verbose=True, preload=True)  # epochs are from -0.8 to 1.2

# ========================================= TFR CALCULATIONS ====================================
# Calculate tfr for post cue alpha
tfr_params = dict(picks=['grad'], use_fft=True, return_itc=False, average=True, decim=2, n_jobs=4, verbose=True)

freqs = np.arange(2,31,1)  # the frequency range over which we perform the analysis
n_cycles = freqs / 2  # the length of sliding window in cycle units. 
time_bandwidth = 2.0  # '(2deltaTdeltaF) number of DPSS tapers to be used + 1.'
                      # 'it relates to the temporal (deltaT) and spectral (deltaF)' 
                      # 'smoothing'
                      # 'the more tapers, the more smooth'->useful for high freq data
                      
tfr_slow_cue_right = mne.time_frequency.tfr_multitaper(epochs['cue_onset_right'],  
                                                  freqs=freqs, 
                                                  n_cycles=n_cycles,
                                                  time_bandwidth=time_bandwidth, 
                                                  **tfr_params                                                  
                                                  )
                                                
tfr_slow_cue_left = mne.time_frequency.tfr_multitaper(epochs['cue_onset_left'],  
                                                  freqs=freqs, 
                                                  n_cycles=n_cycles,
                                                  time_bandwidth=time_bandwidth, 
                                                  **tfr_params                                                  
                                                  )

# Plot TFR on all sensors and check
tfr_slow_cue_right.plot_topo(tmin=-.5, tmax=1.0, 
                        baseline=[-.5,-.3], mode='percent',
                        fig_facecolor='w', font_color='k',
                        vmin=-1, vmax=1, 
                        title='TFR of power < 30Hz - cue right')
tfr_slow_cue_left.plot_topo(tmin=-.5, tmax=1.0,
                         baseline=[-.5,-.3], mode='percent',
                         fig_facecolor='w', font_color='k',
                         vmin=-1, vmax=1, 
                         title='TFR of power < 30Hz - cue left')

# ========================================= A. Peak Alpha Frequency ====================================
# Select occipital sensors
occipital_picks = mne.read_vectorview_selection("occipital")  # contains both mag and grad
occipital_picks =  [channel[-4:] for channel in occipital_picks]  # vectorview selection adds a space in the name of channels!

# Create a list of channel names from epochs.ch_names that have the same last four characters as occipital picks and pick only grads
occipital_channels = [channel for channel in epochs.pick(['grad']).ch_names if channel[-4:] in occipital_picks]

# Crop post stim alpha
tfr_slow_cue_right_post_stim = tfr_slow_cue_right.copy().crop(tmin=0.2,tmax=1.2,fmin=4, fmax=14).pick(occipital_channels)
tfr_slow_cue_left_post_stim = tfr_slow_cue_left.copy().crop(tmin=0.2,tmax=1.2,fmin=4, fmax=14).pick(occipital_channels)

# Find the frequency with the highest power by averaging over sensors and time points (data)
freq_idx_right = np.argmax(np.mean(np.abs(tfr_slow_cue_right_post_stim.data), axis=(0,2)))
freq_idx_left = np.argmax(np.mean(np.abs(tfr_slow_cue_left_post_stim.data), axis=(0,2)))

# Get the corresponding frequencies
peak_freq_cue_right = tfr_slow_cue_right_post_stim.freqs[freq_idx_right]
peak_freq_cue_left = tfr_slow_cue_left_post_stim.freqs[freq_idx_left]

peak_alpha_freq = np.average([peak_freq_cue_right, peak_freq_cue_left])
peak_alpha_freq_range = np.arange(peak_alpha_freq-2, peak_alpha_freq+3)  # for MI calculations
np.savez(peak_alpha_fname, **{'peak_alpha_freq':peak_alpha_freq, 'peak_alpha_freq_range':peak_alpha_freq_range})

# Plot psd and show the peak alpha frequency for this participant
psd_params = dict(picks=occipital_channels, n_jobs=4, verbose=True, fmin=2, fmax=30)
psd_slow_right_post_stim = epochs['cue_onset_right','cue_onset_left'].copy().filter(2,30).compute_psd(**psd_params)

# Average across epochs and get data
psd_slow_right_post_stim_avg = psd_slow_right_post_stim.average()
psds, freqs = psd_slow_right_post_stim_avg.get_data(return_freqs=True)
psds_mean = psds.mean(axis=0)

# Plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(freqs, psds_mean, color='black')
ymin, ymax = ax.get_ylim()
# Indicate peak_alpha_freq_range with a gray shadow
ax.axvline(x=peak_alpha_freq_range[0], 
            color='gray', 
            linestyle='--', 
            linewidth=2)
ax.axvline(x=peak_alpha_freq_range[-1], 
            color='gray', 
            linestyle='--', 
            linewidth=2)
ax.fill_betweenx([ymin, ymax],
                  peak_alpha_freq_range[0], 
                  peak_alpha_freq_range[-1], 
                  color='lightgray', 
                  alpha=0.5)
ax.text(np.max(freqs)-5, np.min(psds_mean)*3, f'PAF = {peak_alpha_freq} Hz', 
         color='black', ha='right', va='bottom')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Power (T/m)^2/Hz')
plt.title('PSDs')

plt.grid(True)
fig_peak_alpha = plt.gcf()
plt.show()

# ========================================= B. ROI ============================================
psd_params = dict(picks=['grad'], n_jobs=4, tmin=0.2, tmax=1.2, fmin=0.1, fmax=60)  # 'remove cue presentation duration from the epoch' 
                                                                                    # '1second = 1Hz frequency resolution for psd calculations'
right_psd = epochs['cue_onset_right'].copy().filter(0.1,60).compute_psd(**psd_params)
left_psd = epochs['cue_onset_left'].copy().filter(0.1,60).compute_psd(**psd_params)

# Get power and frequency data from right sensors
right_psds_right_sens, right_freqs_right_sens = right_psd.copy().pick(right_sensors).get_data(return_freqs=True)  # shape: #epochs, #sensors, #frequencies
left_psds_right_sens, left_freqs_right_sens = left_psd.copy().pick(right_sensors).get_data(return_freqs=True)

# Select alpha and average across epochs
alpha_l_freq, alpha_h_freq = peak_alpha_freq_range[0], peak_alpha_freq_range[-1]
right_alpha_psds_right_sens = right_psds_right_sens[:,:,(right_freqs_right_sens >= alpha_l_freq)
                                                    & (right_freqs_right_sens <= alpha_h_freq)]
right_alpha_psds_right_sens = np.mean(right_alpha_psds_right_sens, axis=(0,2))

left_alpha_psds_right_sens = left_psds_right_sens[:,:,(left_freqs_right_sens >= alpha_l_freq) 
                                                  & (left_freqs_right_sens <= alpha_h_freq)]
left_alpha_psds_right_sens = np.mean(left_alpha_psds_right_sens, axis=(0,2))

# Calculate MI for right sensors and sort
MI_right_sens = (right_alpha_psds_right_sens - left_alpha_psds_right_sens) \
              / (right_alpha_psds_right_sens + left_alpha_psds_right_sens)

MI_right_df = pd.DataFrame({'MI_right': MI_right_sens,
                            'right_sensors': right_sensors})  

# Sort the right MI DataFrame by MI value and extract the first 5 channel names and save the ROI sensors
df_sorted = MI_right_df.sort_values(by='MI_right', ascending=False, key=abs)
MI_right_ROI = df_sorted.head(5) # create a df of MI right ROI sensors and their MI values
MI_right_ROI = MI_right_ROI.sort_index()  # to ensure the order or sensor names is correct in right and left
ROI_right_sens = MI_right_ROI['right_sensors'].tolist() 

# Find the corresponding left sensors 
ROI_symmetric = sensors_layout_df[sensors_layout_df['right_sensors'].isin(ROI_right_sens)]  # reorders channels by channem name
ROI_symmetric.to_csv(ROI_fname, index=False)

ROI_left_sens = ROI_symmetric['left_sensors'].to_list()

# ========================================= LEFT SENSORS =======================================
# Get power and frequency data from right sensors
right_psds_left_ROI_sens, right_freqs_left_ROI_sens = right_psd.copy().pick(ROI_left_sens).get_data(return_freqs=True)  # shape: #epochs, #sensors, #frequencies
left_psds_left_ROI_sens, left_freqs_left_ROI_sens = left_psd.copy().pick(ROI_left_sens).get_data(return_freqs=True)

# Select alpha and average across epochs
right_alpha_psds_left_ROI_sens = right_psds_left_ROI_sens[:,:,(right_freqs_left_ROI_sens >= alpha_l_freq)
                                                    & (right_freqs_left_ROI_sens <= alpha_h_freq)]
right_alpha_psds_left_ROI_sens = np.mean(right_alpha_psds_left_ROI_sens, axis=(0,2))

left_alpha_psds_left_ROI_sens = left_psds_left_ROI_sens[:,:,(left_freqs_left_ROI_sens >= alpha_l_freq) 
                                                  & (left_freqs_left_ROI_sens <= alpha_h_freq)]
left_alpha_psds_left_ROI_sens = np.mean(left_alpha_psds_left_ROI_sens, axis=(0,2))

# Calculate MI for right sensors and sort
MI_left_ROI_sens = (right_alpha_psds_left_ROI_sens - left_alpha_psds_left_ROI_sens) \
                 / (right_alpha_psds_left_ROI_sens + left_alpha_psds_left_ROI_sens)

MI_left_ROI = pd.DataFrame({'MI_left':MI_left_ROI_sens,
                            'left_sensors':ROI_left_sens})  

# ========================================= ALI =======================================
ALI = np.mean(MI_right_ROI['MI_right']) - np.mean(MI_left_ROI['MI_left'])
ROI_ALI_df = pd.DataFrame({'ALI_avg_ROI':[ALI]})  # scalars should be lists for dataframe conversion

# Save and read the dataframe as html for the report
ROI_ALI_df.to_html(ROI_MI_ALI_html)
with open(ROI_MI_ALI_html, 'r') as f:
    html_string = f.read()

# ========================================= RIGHT SENSORS- not complete =======================================
# Pick alpha on right sensors for ROI-- the order of sensors is based on the list you provided
tfr_alpha_right_cue_right_sens = tfr_slow_cue_right.copy().pick(right_sensors).crop(fmin=alpha_l_freq, fmax=alpha_h_freq)
tfr_alpha_left_cue_right_sens = tfr_slow_cue_left.copy().pick(right_sensors).crop(fmin=alpha_l_freq, fmax=alpha_h_freq)

# Plot and check
tfr_alpha_right_cue_right_sens.plot_topo(tmin=-.5, tmax=1.0, 
                                        baseline=[-.5,-.3], mode='percent',
                                        fig_facecolor='w', font_color='k',
                                        vmin=-1, vmax=1, 
                                        title='TFR of power of alpha - cue right')
tfr_alpha_left_cue_right_sens.plot_topo(tmin=-.5, tmax=1.0,
                                        baseline=[-.5,-.3], mode='percent',
                                        fig_facecolor='w', font_color='k',
                                        vmin=-1, vmax=1, 
                                        title='TFR of power of alpha - cue left')

# Calculate MI using power data
MI_right_sens = tfr_alpha_right_cue_right_sens.copy()
MI_right_sens.data = (tfr_alpha_right_cue_right_sens.data - tfr_alpha_left_cue_right_sens.data) \
                   / (tfr_alpha_right_cue_right_sens.data + tfr_alpha_left_cue_right_sens.data)

MI_right_sens.plot_topo(tmin=-.5, tmax=1.0,
                        baseline=[-.5,-.3], mode='percent',
                        fig_facecolor='w', font_color='k',
                        vmin=-1, vmax=1, 
                        title='MI of alpha - right sensors')
# =================================================================================================================

if summary_rprt:
    report_root = op.join(mTBI_root, r'results-outputs/mne-reports')  # RDS folder for reports
    report_folder = op.join(report_root , 'sub-' + subject, 'task-' + task)

    report_fname = op.join(report_folder, 
                        f'mneReport_sub-{subject}_{task}.hdf5')    # it is in .hdf5 for later adding images
    html_report_fname = op.join(report_folder, f'report_preproc_{task}.html')

    report = mne.open_report(report_fname)

    report.add_figure(fig=fig_peak_alpha, title='PSD and PAF',
                     caption='range of peak alpha frequency on \
                     occipital gradiometers', 
                     tags=('tfr'),
                     section='TFR'  # only in ver 1.1
                     )
    report.add_html(html=html_string, 
                   section='ALI',  # only in ver 1.1
                   title='Primary Outcome',
                   tags=('ali')
                   )
    report.save(report_fname, overwrite=True)
    report.save(html_report_fname, overwrite=True, open_browser=True)  # to check how the report looks





