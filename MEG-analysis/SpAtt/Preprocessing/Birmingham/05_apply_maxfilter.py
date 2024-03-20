# -*- coding: utf-8 -*-
"""
===============================================
05. Applying MaxFilter

this code uses MaxFilter to reduce artifacts from
environmental sources and sensor noise

written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:
    1) generate the report and save concat files
    again
Questions:
    1) 
    2) raw.info['dev_head_t'] is not align for 
    two runs. what should be done?
    3) how come there are more gradio and
    magneto sensors after filtering?
"""

import os
import os.path as op
import matplotlib.pyplot as plt
import numpy as np

import mne
from mne_bids import BIDSPath, read_raw_bids
import mne.preprocessing as preproc

# fill these out
site = 'Birmingham'
subject = '2004'  # subject code in mTBI project
session = '04B'  # data collection session within each run
run = '01'  # data collection run for each participant
task = 'SpAtt'
meg_suffix = 'meg'
meg_extension = '.fif'
deriv_suffix = 'raw_sss'
head_pos_suffix = 'head_pos'  # name for headposition file

tsss = False  # sss or tsss?
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
                     task=task, run=run, root=bids_root, datatype='meg',
                     suffix=meg_suffix, extension=meg_extension)
bids_fname = bids_path.basename.replace(meg_suffix, deriv_suffix)  # only used for suffices that are not recognizable to bids 

deriv_root = op.join(bids_root, 'derivatives')  # RDS folder for results
if not op.exists(op.join(deriv_root , 'sub-' + subject, 'task-' + task)):
    os.makedirs(op.join(deriv_root , 'sub-' + subject, 'task-' + task))
deriv_folder = op.join(deriv_root , 'sub-' + subject, 'task-' + task)
deriv_fname = op.join(deriv_folder, bids_fname)
head_pos_fname = deriv_fname.replace(deriv_suffix, head_pos_suffix)

# Define the fine calibration and cross-talk compensation files 
crosstalk_file = op.join(bids_path.directory, 'sub-' + subject +'_ses-' + session + 
                         '_acq-crosstalk_meg.fif')  
calibration_file = op.join(bids_path.directory, 'sub-' + subject +'_ses-' + session + 
                           '_acq-calibration_meg.dat')  

# read and raw data 
"""only do the if run==2 for this part (as an example) for other sections
 do it manually, unless you have many 2-run subjects"""
if run == '02':
    bids_path2 = bids_path.copy().update(run='02')
    if op.exists(bids_path2):    
       raw1 = read_raw_bids(bids_path=bids_path, extra_params={'preload':True},
                               verbose=True)  #'fif files will be read with'
                                              #'allow_maxshield=True by default'                          
       raw2 = read_raw_bids(bids_path=bids_path2, extra_params={'preload':True},
                        verbose=True)
       raw2.info['dev_head_t'] = raw1.info['dev_head_t']  # to solve the error about head position not being aligned
       raw = mne.io.concatenate_raws([raw1, raw2])
else:
   raw = read_raw_bids(bids_path=bids_path, extra_params={'preload':True},
                           verbose=True)

# Identify and show faulty sensors using max filtering 
"""to identify bad channels it is best to use concatenated files (in case of
multiple meg files) and then run the maxfilter for files separately (works
better on separate files) 
"""
auto_noisy_chs, auto_flat_chs, auto_scores = preproc.find_bad_channels_maxwell(
    raw.copy(), cross_talk=crosstalk_file, calibration=calibration_file,
    return_scores=True, verbose=True)

print('noisy = ', auto_noisy_chs)
print('flat = ', auto_flat_chs)
len(auto_noisy_chs) + len(auto_flat_chs)

# set noisy and flat channels as 'bads' in the data set
raw.info['bads'] = []
raw.info['bads'].extend(auto_noisy_chs + auto_flat_chs)
print('bads = ', raw.info['bads'])
len(raw.info['bads'])

# we might need to change MEGIN magnetometer coil types (type 3022 and 3023 to 3024) 
# to ensure compatibility across systems
raw.fix_mag_coil_types()

if not tsss:  # which maxwell filtering to use? sss or tsss
    # Apply the Maxfilter with fine calibration and cross-talk reduction (SSS)
    raw_sss = preproc.maxwell_filter(raw, cross_talk=crosstalk_file,
                                     calibration=calibration_file, verbose=True)
    
elif tsss:  
    # Apply Spatiotemporal SSS by passing st_duration to maxwell_filter
    raw_sss = preproc.maxwell_filter(raw, cross_talk=crosstalk_file, st_duration=20,
                                     calibration=calibration_file, verbose=True)

if test_plot:
    # Plot power spectra of raw data and after maxwell filterting for comparison
    fig, ax = plt.subplots(2,2)

    fig = raw.compute_psd(fmax=60, n_fft=1000).plot(axes=ax[:,0], show=False)
    fig = raw_sss.compute_psd(fmax=60, n_fft=1000).plot(axes=ax[:,1], show=False)

    ax[1,0].set_xlabel(' \nPSD before filtering')
    ax[1,1].set_xlabel(' \nPSD after filtering')
    fig.set_tight_layout(True)
    plt.show()

# Plotting head position during each run using cHPI info
chpi_freqs, ch_idx, chpi_codes = mne.chpi.get_chpi_info(info=raw.info)
print(f"cHPI coil frequencies extracted from raw: {chpi_freqs} Hz")

# Get amplitude of cHPI
chpi_amplitudes = mne.chpi.compute_chpi_amplitudes(raw)

# Compute time-varying HPI coil locations from amplitudes
chpi_locs = mne.chpi.compute_chpi_locs(raw.info, chpi_amplitudes)

# Compute head position from the coil locations
"""
These head positions can then be used with mne.preprocessing.maxwell_filter()
to compensate for movement, or with mne.preprocessing.annotate_movement() to
mark segments as bad that deviate too much from the average head position.
"""
head_pos = mne.chpi.compute_head_pos(raw.info, chpi_locs, verbose=True)
mne.chpi.write_head_pos(head_pos_fname, head_pos)

# Calculate one output for head position
""" 
Average across all timepoints for x, y, and z
which are head_pos[:,4:7]. then calculate the combined
movement in three axes and average and std
"""
head_pos_avg_three_planes = np.mean(head_pos[:,4:7],axis=0)
head_pos_std_three_planes = np.std(head_pos[:,4:7],axis=0)
head_pos_avg_cmbnd_three_planes = np.sqrt(np.sum(head_pos_avg_three_planes**2))
head_pos_std_cmbnd_three_planes = np.sqrt(np.sum(head_pos_std_three_planes**2))


fig, axs = plt.subplots(figsize=(10, 6))
mne.viz.plot_head_positions(head_pos, mode="traces", show=False)
# Plot average_movement as an annotation
plt.annotate(f'Average movement: {head_pos_avg_cmbnd_three_planes:.2f}', xy=(0.1, 0.2), xycoords='axes fraction')

# Plot std_dev_movement as an annotation
plt.annotate(f'Std deviation of movement: {head_pos_std_cmbnd_three_planes:.2f}', xy=(0.1, 0.05), xycoords='axes fraction')

fig_head_pos = plt.gcf()
# Show the plot
plt.show()

# Remove cHPI frequencies and save sss/tsss file
raw_sss_filtered = raw_sss.copy().filter(0.3,100)  
raw_sss_filtered.save(deriv_fname, overwrite=True)

if summary_rprt:
    report_root = op.join(mTBI_root, 'results-outputs/mne-reports')  # RDS folder for reports
   
    if not op.exists(op.join(report_root , 'sub-' + subject, 'ses-' + session, 'task-' + task)):
        os.makedirs(op.join(report_root , 'sub-' + subject, 'ses-' + session, 'task-' + task))
    report_folder = op.join(report_root , 'sub-' + subject, 'ses-' + session, 'task-' + task)

    report_fname = op.join(report_folder, 
                        f'mneReport_sub-{subject}_{session}_{task}_1.hdf5')    # it is in .hdf5 for later adding images
    html_report_fname = op.join(report_folder, f'report_preproc_{session}_{task}_1.html')
    
    # Filter raw data to become similar to sss for the report
    raw.filter(0.3,100)

    # Create the report for the first time
    report = mne.Report(title=f'Subject n.{subject}- {task}')
    report.add_raw(raw=raw, title='Raw <60Hz', 
                    psd=True, butterfly=False, tags=('raw'))
    report.add_raw(raw=raw_sss_filtered, title='Max filter (sss) <60Hz', 
                    psd=True, butterfly=False, tags=('MaxFilter'))
    report.add_figure(fig_head_pos, title="head position over time",
                        tags=('cHPI'), image_format="PNG")
    report.save(report_fname, overwrite=True)
    report.save(html_report_fname, overwrite=True, open_browser=True)  # to check how the report looks


































