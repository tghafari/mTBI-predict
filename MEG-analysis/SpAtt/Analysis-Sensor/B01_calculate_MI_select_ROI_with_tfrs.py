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
    4. calculate tfr for right sensors 
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
subject = '2008'  # subject code in mTBI project
session = '02B'  # data collection session within each run
run = '01'  # data collection run for each participant
task = 'SpAtt'
meg_extension = '.fif'
meg_suffix = 'meg'
input_suffix = 'epo'
deriv_suffix = 'psd'

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
ROI_dir = op.join(mTBI_root, 'results-outputs/group-analysis/task-SpAtt/lateralisation-indices')
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
MI_ALI_fname = op.join(ROI_dir, f'sub-{subject}_MI_ALI.csv')
ROI_MI_ALI_fname = op.join(ROI_dir, f'sub-{subject}_ROI_MI_ALI.csv')
ROI_MI_ALI_html =  op.join(ROI_dir, f'sub-{subject}_ROI_MI_ALI.html')

peak_alpha_fname = op.join(ROI_dir, f'sub-{subject}_peak_alpha.npz')  # 2 numpy arrays saved into an uncompressed file
# Read sensor layout sheet from camcan RDS
"""these variables are in correct right-and-left-corresponding-sensors order"""
sensors_layout_sheet = op.join(mTBI_root, 'results-outputs/sensor_layout_name_grad_no_central.csv')
sensors_layout_names_df = pd.read_csv(sensors_layout_sheet)

right_sensors = [ch[1:8] for ch in sensors_layout_names_df['right_sensors']]
left_sensors = [ch[1:8] for ch in sensors_layout_names_df['left_sensors']]
sensors_layout_df = pd.DataFrame({'left_sensors': left_sensors,
                                  'right_sensors': right_sensors})  

# Read epoched data
epochs = mne.read_epochs(input_fname, verbose=True, preload=True)  # epochs are from -0.8 to 1.2

# ========================================= TFR CALCULATIONS AND FIRST PLOT (PLOT_TOPO) ====================================
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
fig_plot_topo_right = tfr_slow_cue_right.plot_topo(tmin=-.5, 
                                                   tmax=.8, 
                                                   baseline=[-.5,0], 
                                                   mode='percent',
                                                   fig_facecolor='w', 
                                                   font_color='k',
                                                   vmin=-1, 
                                                   vmax=1, 
                                                   title='TFR of power < 30Hz - cue right')
fig_plot_topo_left = tfr_slow_cue_left.plot_topo(tmin=-.5, 
                                                 tmax=.8,
                                                 baseline=[-.5,0], 
                                                 mode='percent',
                                                 fig_facecolor='w', 
                                                 font_color='k',
                                                 vmin=-1, 
                                                 vmax=1, 
                                                 title='TFR of power < 30Hz - cue left')

# ========================================= SECOND PLOT (REPRESENTATIVE SENSROS) ====================================
# Plot TFR for representative sensors - same in all participants
fig_tfr, axis = plt.subplots(2, 2, figsize = (7, 7))
sensors = ['MEG1733','MEG2133','MEG1943','MEG2533']

for idx, sensor in enumerate(sensors):
    if idx < len(sensors)/2:
        tfr_slow_cue_left.plot(picks=sensor, 
                               baseline=[-.5,0],
                               mode='percent', 
                               tmin=-.5, 
                               tmax=1.0,
                               vmin=-.75, 
                               vmax=.75,
                               axes=axis[idx,0], 
                               show=False)
        axis[idx, 0].set_title(f'cue left-{sensor}')        
    else:   
        tfr_slow_cue_right.plot(picks=sensor,
                                baseline=[-.5,0],
                                mode='percent', 
                                tmin=-.5, 
                                tmax=1.0,
                                vmin=-.75, 
                                vmax=.75, 
                                axes=axis[idx-2,1], 
                                show=False)
        axis[idx-2, 1].set_title(f'cue right-{sensor}') 
        
axis[0, 0].set_ylabel('left sensors')  
axis[1, 0].set_ylabel('right sensors')  
axis[0, 1].set_ylabel('left sensors')  
axis[1, 1].set_ylabel('right sensors')
axis[0, 0].set_xlabel('')  # Remove x-axis label for top plots
axis[0, 1].set_xlabel('')


fig_tfr.set_tight_layout(True)
plt.show()      

# ========================================= PEAK ALPHA FREQUENCY (PAF) AND THIRD PLOT ====================================
# Select occipital sensors
occipital_picks = mne.read_vectorview_selection("occipital")  # contains both mag and grad
occipital_picks =  [channel[-4:] for channel in occipital_picks]  # vectorview selection adds a space in the name of channels!

# Create a list of channel names from epochs.ch_names that have the same last four characters as occipital picks and pick only grads
occipital_channels = [channel for channel in epochs.pick(['grad']).ch_names if channel[-4:] in occipital_picks]

# Crop post stim alpha
tfr_slow_cue_right_post_stim = tfr_slow_cue_right.copy().crop(tmin=.2,tmax=.8,fmin=4, fmax=14).pick(occipital_channels)
tfr_slow_cue_left_post_stim = tfr_slow_cue_left.copy().crop(tmin=.2,tmax=.8,fmin=4, fmax=14).pick(occipital_channels)

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
n_fft = int((epochs.tmax - epochs.tmin)*1000)
psd_params = dict(picks=occipital_channels, method="welch", fmin=1, fmax=60, n_jobs=4, verbose=True, n_fft=n_fft, n_overlap=int(n_fft/2))
psd_slow_right_post_stim = epochs['cue_onset_right','cue_onset_left'].copy().compute_psd(**psd_params)

# Average across epochs and get data
psd_slow_right_post_stim_avg = psd_slow_right_post_stim.average()
psds, freqs = psd_slow_right_post_stim_avg.get_data(return_freqs=True)
psds_mean = psds.mean(axis=0)

# Plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(freqs[0:int(len(freqs)/2)], psds_mean[0:int(len(freqs)/2)], color='black')  # remove frequencies higher than 30Hz for plotting
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
ax.text(np.max(freqs)-5, 
        np.min(psds_mean)*3, 
        f'PAF = {peak_alpha_freq} Hz', 
        color='black', 
        ha='right', 
        va='bottom')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Power (T/m)^2/Hz')
plt.title(f'PSDs- PAF = {peak_alpha_freq} Hz')

plt.grid(True)
fig_peak_alpha = plt.gcf()
plt.show()

# ========================================= TOPOGRAPHIC MAPS AND FOURTH PLOT ============================================
# Plot post cue peak alpha range topographically
topomap_params = dict(fmin=peak_alpha_freq_range[0], 
                      fmax=peak_alpha_freq_range[-1],
                      tmin=.2,
                      tmax=.8,
                      vlim=(-.5,.5),
                      baseline=(-.5, -.3), 
                      mode='percent', 
                      ch_type='grad',)

fig_topo, axis = plt.subplots(1, 2, figsize=(7, 4))
tfr_slow_cue_left.plot_topomap(**topomap_params,
                           axes=axis[0],
                           show=False)
tfr_slow_cue_right.plot_topomap(**topomap_params,
                            axes=axis[1],
                            show=False)
axis[0].title.set_text('cue left')
axis[1].title.set_text('cue right')
fig_topo.suptitle("Post stim alpha (PAF)")
fig_topo.set_tight_layout(True)
plt.show()

# ========================================= B. RIGHT SENSORS and ROI ============================================
tfr_alpha_params = dict(picks='grad', use_fft=True, return_itc=False, average=True, decim=2, n_jobs=4, verbose=True)
tfr_params = dict(picks=['grad'], use_fft=True, return_itc=False, average=True, decim=2, n_jobs=4, verbose=True)

freqs = peak_alpha_freq_range  # peak frequency range calculated earlier
n_cycles = freqs / 2  # the length of sliding window in cycle units. 
time_bandwidth = 2.0 
                      
tfr_right_alpha_all_sens = mne.time_frequency.tfr_multitaper(epochs['cue_onset_right'],  
                                                  freqs=freqs, 
                                                  n_cycles=n_cycles,
                                                  time_bandwidth=time_bandwidth, 
                                                  **tfr_params,
                                                  )                                                
tfr_left_alpha_all_sens = mne.time_frequency.tfr_multitaper(epochs['cue_onset_left'],  
                                                  freqs=freqs, 
                                                  n_cycles=n_cycles,
                                                  time_bandwidth=time_bandwidth, 
                                                  **tfr_params,
                                                  )   

# Crop tfrs to post-stim alpha and right sensors
tfr_right_post_stim_alpha_right_sens = tfr_right_alpha_all_sens.copy().pick(right_sensors).crop(tmin=.2, tmax=.8)
tfr_left_post_stim_alpha_right_sens = tfr_left_alpha_all_sens.copy().pick(right_sensors).crop(tmin=.2, tmax=.8)

# Calculate power modulation for attention right and left (always R- L)
tfr_alpha_MI_right_sens = tfr_right_post_stim_alpha_right_sens.copy()
tfr_alpha_MI_right_sens.data = (tfr_right_post_stim_alpha_right_sens.data - tfr_left_post_stim_alpha_right_sens.data) \
    / (tfr_right_post_stim_alpha_right_sens.data + tfr_left_post_stim_alpha_right_sens.data)  # shape: #sensors, #freqs, #time points

# Average across time points and alpha frequencies
tfr_avg_alpha_MI_right_sens_power = np.mean(tfr_alpha_MI_right_sens.data, axis=(1,2))   # the order of channels is the same as right_sensors (I double checked)

# Save to dataframe
MI_right_sens_df = pd.DataFrame({'MI_right': tfr_avg_alpha_MI_right_sens_power,
                                 'right_sensors': right_sensors})  

# Sort the right MI DataFrame by MI value and extract the first 5 channel names and save the ROI sensors
df_sorted = MI_right_sens_df.sort_values(by='MI_right', ascending=False, key=abs)
MI_right_ROI = df_sorted.head(5) # create a df of MI right ROI sensors and their MI values
MI_right_ROI = MI_right_ROI.sort_index()  # to ensure the order or sensor names is correct in right and left
ROI_right_sens = MI_right_ROI['right_sensors'].tolist() 

# Find the corresponding left sensors 
ROI_symmetric = sensors_layout_df[sensors_layout_df['right_sensors'].isin(ROI_right_sens)]  # reorders channels by channem name
ROI_symmetric.to_csv(ROI_fname, index=False)

ROI_left_sens = ROI_symmetric['left_sensors'].to_list()

# Calculate MI for right ROI for later plotting
tfr_right_post_stim_alpha_right_ROI_sens = tfr_right_alpha_all_sens.copy().pick(ROI_right_sens).crop(tmin=0.2, tmax=.8)
tfr_left_post_stim_alpha_right_ROI_sens = tfr_left_alpha_all_sens.copy().pick(ROI_right_sens).crop(tmin=0.2, tmax=.8)

tfr_alpha_MI_right_ROI = tfr_right_post_stim_alpha_right_ROI_sens.copy()
tfr_alpha_MI_right_ROI.data = (tfr_right_post_stim_alpha_right_ROI_sens.data - tfr_left_post_stim_alpha_right_ROI_sens.data) \
    / (tfr_right_post_stim_alpha_right_ROI_sens.data + tfr_right_post_stim_alpha_right_ROI_sens.data)  # shape: #sensors, #freqs, #time points

# ========================================= LEFT SENSORS and ROI ON TOPOMAP (FIFTH PLOT) =======================================
# Crop tfrs to post-stim alpha and right sensors
tfr_right_post_stim_alpha_left_ROI_sens = tfr_right_alpha_all_sens.copy().pick(ROI_left_sens).crop(tmin=0.2, tmax=.8)
tfr_left_post_stim_alpha_left_ROI_sens = tfr_left_alpha_all_sens.copy().pick(ROI_left_sens).crop(tmin=0.2, tmax=.8)

# Calculate power modulation for attention right and left (always R- L)
tfr_alpha_MI_left_ROI = tfr_left_post_stim_alpha_left_ROI_sens.copy()
tfr_alpha_MI_left_ROI.data = (tfr_right_post_stim_alpha_left_ROI_sens.data - tfr_left_post_stim_alpha_left_ROI_sens.data) \
    / (tfr_right_post_stim_alpha_left_ROI_sens.data + tfr_left_post_stim_alpha_left_ROI_sens.data)  # shape: #sensors, #freqs, #time points

# Average across time points and alpha frequencies
tfr_avg_alpha_MI_left_ROI_power = np.mean(tfr_alpha_MI_left_ROI.data, axis=(1,2))   # the order of channels is the same as right_sensors (I double checked)

# Save to dataframe
MI_left_ROI_df = pd.DataFrame({'MI_left': tfr_avg_alpha_MI_left_ROI_power,
                               'left_sensors': ROI_left_sens})  

# Plot MI on topoplot with highlighted ROI sensors
tfr_alpha_modulation_power= tfr_right_alpha_all_sens.copy()
tfr_alpha_modulation_power.data = (tfr_right_alpha_all_sens.data - tfr_left_alpha_all_sens.data) \
                                / (tfr_right_alpha_all_sens.data + tfr_left_alpha_all_sens.data)

sensors = np.concatenate((ROI_symmetric['right_sensors'].values, 
                          ROI_symmetric['left_sensors'].values), axis=0)

fig, ax = plt.subplots()
fig_mi = tfr_alpha_modulation_power.plot_topomap(tmin=.2, 
                                                 tmax=.8, 
                                                 fmin=peak_alpha_freq_range[0],
                                                 fmax=peak_alpha_freq_range[1],
                                                 vlim=(-.2,.2),
                                                 show=False, axes=ax)
# Plot markers for the sensors in ROI_right_sens
for sensor in sensors:
    ch_idx = tfr_alpha_modulation_power.info['ch_names'].index(sensor)
    x, y = tfr_alpha_modulation_power.info['chs'][ch_idx]['loc'][:2]
    ax.plot(x, y, 'ko', markerfacecolor='none', markersize=10)
                                 
fig_mi.suptitle('attention right - attention left (PAF range on gradiometers)')
plt.show()  

# ========================================= MI OVER TIME AND SIXTH PLOT =======================================
# Plot MI avg across ROI over time
fig, axs = plt.subplots(1, 2, figsize=(12, 6))

# Plot average power and std for tfr_alpha_MI_left_ROI
axs[0].plot(tfr_alpha_MI_left_ROI.times, tfr_alpha_MI_left_ROI.data.mean(axis=(0, 1)), label='Average MI', color='red')
axs[0].fill_between(tfr_alpha_MI_left_ROI.times,
                    tfr_alpha_MI_left_ROI.data.mean(axis=(0, 1)) - tfr_alpha_MI_left_ROI.data.std(axis=(0, 1)),
                    tfr_alpha_MI_left_ROI.data.mean(axis=(0, 1)) + tfr_alpha_MI_left_ROI.data.std(axis=(0, 1)),
                    color='red', alpha=0.3, label='Standard Deviation')
axs[0].set_title('MI on left ROI')
axs[0].set_xlabel('Time (s)')
axs[0].set_ylabel('Average MI (PAF)')
axs[0].set_ylim(min(tfr_alpha_MI_left_ROI.data.mean(axis=(0, 1))) - 0.3, 
                    max(tfr_alpha_MI_left_ROI.data.mean(axis=(0, 1))) + 0.3)
axs[0].legend()

# Plot average power and std for tfr_alpha_MI_right_ROI
axs[1].plot(tfr_alpha_MI_right_ROI.times, tfr_alpha_MI_right_ROI.data.mean(axis=(0, 1)), label='Average MI', color='blue')
axs[1].fill_between(tfr_alpha_MI_right_ROI.times,
                    tfr_alpha_MI_right_ROI.data.mean(axis=(0, 1)) - tfr_alpha_MI_right_ROI.data.std(axis=(0, 1)),
                    tfr_alpha_MI_right_ROI.data.mean(axis=(0, 1)) + tfr_alpha_MI_right_ROI.data.std(axis=(0, 1)),
                    color='blue', alpha=0.3, label='Standard Deviation')
axs[1].set_title('MI on right ROI')
axs[1].set_xlabel('Time (s)')
axs[1].set_ylabel('Average MI (PAF)')
axs[0].set_ylim(min(tfr_alpha_MI_right_ROI.data.mean(axis=(0, 1))) - 0.3, 
                    max(tfr_alpha_MI_right_ROI.data.mean(axis=(0, 1))) + 0.3)
axs[1].legend()

# Adjust layout
plt.tight_layout()

# Save the figure in a variable
fig_mi_overtime = fig

# Show plot (optional)
plt.show()


# ========================================= ALI AND PRIMARY OUTCOME (LAST OUTPUT) =======================================
ALI = np.mean(MI_right_ROI['MI_right']) - np.mean(MI_left_ROI_df['MI_left'])
ROI_ALI_df = pd.DataFrame({'ALI_avg_ROI':[ALI]})  # scalars should be lists for dataframe conversion

# Save and read the dataframe as html for the report
ROI_ALI_df.to_html(ROI_MI_ALI_html)
with open(ROI_MI_ALI_html, 'r') as f:
    html_string = f.read()

# =================================================================================================================

if summary_rprt:
    report_root = op.join(mTBI_root, 'results-outputs/mne-reports')  # RDS folder for reports
    if not op.exists(op.join(report_root , 'sub-' + subject, 'ses-' + session, 'task-' + task)):
        os.makedirs(op.join(report_root , 'sub-' + subject, 'ses-' + session, 'task-' + task))
    report_folder = op.join(report_root , 'sub-' + subject, 'ses-' + session, 'task-' + task)

    report_fname = op.join(report_folder, 
                        f'mneReport_sub-{subject}_{session}_{task}_1.hdf5')    # it is in .hdf5 for later adding images
    html_report_fname = op.join(report_folder, f'report_preproc_{session}_{task}_1.html')

    report = mne.open_report(report_fname)
    report.add_figure(fig=fig_plot_topo_right, title='TFR of power < 30Hz - cue right',
                    caption='Time Frequency Representation for \
                    cue right- -0.5 to 0.8- baseline corrected', 
                    tags=('tfr'),
                    section='TFR'  # only in ver 1.1
                    )
    report.add_figure(fig=fig_plot_topo_left, title='TFR of power < 30Hz - cue left',
                    caption='Time Frequency Representation for \
                        cue left- -0.5 to 0.8- baseline corrected', 
                    tags=('tfr'),
                    section='TFR'  # only in ver 1.1
                    )
    report.add_figure(fig=fig_tfr, title='TFR on four sensors',
                    caption='Time Frequency Representation on \
                    right and left sensors', 
                    tags=('tfr'),
                    section='TFR'  # only in ver 1.1
                    )
    report.add_figure(fig=fig_peak_alpha, title='PSD and PAF',
                     caption='range of peak alpha frequency on \
                        occipital gradiometers', 
                     tags=('tfr'),
                     section='TFR'  # only in ver 1.1
                     )
    report.add_figure(fig=fig_topo, title='post stim alpha',
                     caption='PAF range (grad), 0.2-0.8sec, \
                        baseline corrected', 
                     tags=('tfr'),
                     section='TFR'  # only in ver 1.1
                     )   
    report.add_figure(fig=fig_mi, title='MI and ROI',
                     caption='MI on PAF range and \
                        ROI sensors (grads - 0.2 to 0.8 sec)', 
                     tags=('ali'),
                     section='ALI'  
                     )  
    report.add_figure(fig=fig_mi_overtime, title='MI over time',
                     caption='MI average on ROI in PAF \
                     range- grads', 
                     tags=('ali'),
                     section='ALI'  
                     )
    report.add_html(html=html_string, 
                     section='ALI',  
                     title='Primary Outcome',
                     tags=('ali')
                     )
    report.save(report_fname, overwrite=True)
    report.save(html_report_fname, overwrite=True, open_browser=True)  # to check how the report looks





