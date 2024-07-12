# -*- coding: utf-8 -*-
"""
===============================================
P02. Applying MaxFilter

this code uses MaxFilter to reduce artifacts from
environmental sources and sensor noise. 
This is part of the automated preprocessing
pipeline.

written by Tara Ghafari
adapted from oscfer88
==============================================
"""

import os
import os.path as op
import matplotlib.pyplot as plt
import numpy as np

import mne
from mne_bids import BIDSPath, read_raw_bids
import mne.preprocessing as preproc
from copy import deepcopy

from config import st_duration, session_info, directories


def get_bad_sensors_from_user(original_bads, raw, plot_bads=True):
    """this function will get the number of bad ICA components
    from the user to exclude from the data."""
    
    bad_sensors = []
    while True:
        user_bads = input("Enter full name of bad sensors if you have \
                            additional ones that were not detected by \
                            maxwell(or press 'd' to finish):")
        if user_bads.lower() == 'd':
            break
        try:
            bad_sensor = str(user_bads)  # Convert the input to a string
            bad_sensors.append(bad_sensor)
        except ValueError:
            print("Invalid input. Please enter a valid sensor name.")
    
    if len(user_bads) != 0:
        if plot_bads:
            raw.copy().pick(user_bads + original_bads).compute_psd().plot()  # double check bad channels
        if len(user_bads) > 1:
            raw.info["bads"].extend(user_bads)
        elif len(user_bads) == 1:
            raw.info["bads"].append(user_bads)  # add a single channel 
    elif len(user_bads) == 0:
        if plot_bads:
            raw.copy().pick(original_bads).compute_psd().plot()

    return bad_sensors


# fill these out
deriv_suffix = 'raw_sss'
head_pos_suffix = 'head_pos'  # name for headposition file

test_plot = False  # do you want to plot the data to test (True) or just generate report (False)?

bids_path = BIDSPath(subject=session_info.subject, 
                     session=session_info.session, 
                     task=session_info.task, 
                     run=session_info.run, 
                     datatype ='meg',
                     suffix='meg', 
                     extension='.fif',
                     root=directories.bids_root)


input_fname = bids_path.basename.replace(meg_suffix, deriv_suffix)  # only used for suffices that are not recognizable to bids 
deriv_fname = op.join(deriv_folder, input_fname)
head_pos_fname = deriv_fname.replace(deriv_suffix, head_pos_suffix)

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
    raw.copy(), cross_talk=bids_path.meg_crosstalk_fpath, calibration=bids_path.meg_calibration_fpath,
    return_scores=True, verbose=True)

print('noisy = ', auto_noisy_chs)
print('flat = ', auto_flat_chs)

# set noisy and flat channels as 'bads' in the data set
raw.info['bads'] = []
raw.info['bads'].extend(auto_noisy_chs + auto_flat_chs)
original_bads = deepcopy(raw.info["bads"])
print('these are the bad sensors from maxwell: ', original_bads)
user_bads = get_bad_sensors_from_user(original_bads, raw)


# we might need to change MEGIN magnetometer coil types (type 3022 and 3023 to 3024) 
# to ensure compatibility across systems
raw.fix_mag_coil_types()

coord_frame = 'meg'  # set coordinate frame
    
# Apply the Maxfilter with fine calibration and cross-talk reduction (SSS)
raw_sss = preproc.maxwell_filter(raw, 
                                 cross_talk=bids_path.meg_crosstalk_fpath,
                                 calibration=bids_path.meg_calibration_fpath, 
                                 st_duration=st_duration,
                                 origin='auto',
                                 coord_frame=coord_frame, 
                                 verbose=True)
    
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

report_root = op.join(mTBI_root, 'results-outputs/mne-reports')  # RDS folder for reports
if not op.exists(op.join(report_root , 'sub-' + subject, 'ses-' + session, 'task-' + task)):
    os.makedirs(op.join(report_root , 'sub-' + subject, 'ses-' + session, 'task-' + task))
report_folder = op.join(report_root , 'sub-' + subject, 'ses-' + session, 'task-' + task)

report_input = input("Do you want the output plot to be added to the \
                        participant's report? (y/n)")

if report_input == 'n':
    html_report_fname = op.join(report_folder, f'report_preproc_{session}_{task}_maxwell.html')
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
    report.save(html_report_fname, overwrite=True, open_browser=True)  # to check how the report looks

    full_report_input = input("Do you want to add this to the full report now? (y/n)")
    if full_report_input == 'y':
        report_fname = op.join(report_folder, 
                    f'mneReport_sub-{subject}_{session}_{task}_full.hdf5') 
        report.save(report_fname, overwrite=True)

elif report_input == 'y':
    report_fname = op.join(report_folder, 
                        f'mneReport_sub-{subject}_{session}_{task}_full.hdf5')    # it is in .hdf5 for later adding images
    
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





























