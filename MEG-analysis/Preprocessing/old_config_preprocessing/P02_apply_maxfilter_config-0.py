# -*- coding: utf-8 -*-
"""
===============================================
P02. Applying MaxFilter_config

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

from config import Config

# Initialize the config
config = Config()

def get_bad_sensors_from_user(original_bads, raw, plot_bads=True):
    """    
    Get bad sensors from the user and add them to the raw data info.
    
    Args:
        original_bads (list): Original bad sensors detected by Maxwell.
        raw (mne.io.Raw): Raw data object.
        plot_bads (bool): Whether to plot the bad sensors.
    
    Returns:
        list: User-provided bad sensors.
    """
    
    bad_sensors = []
    while True:
        print('These are the bad sensors from maxwell: ', original_bads)
        user_bads = input("Enter full name of bad sensors if you have \
                            additional ones that were not detected by \
                            maxwell (eg. 'MEG1323') or press 'd' to finish:")
        if user_bads.lower() == 'd':
            break
        try:
            bad_sensor = str(user_bads)  # Convert the input to a string
            bad_sensors.append(bad_sensor)
        except ValueError:
            print("Invalid input. Please enter a valid sensor name.")
    
    if bad_sensors:
        if plot_bads:
            raw.copy().pick(bad_sensors).compute_psd().plot(title='user added bad channels')  # double check bad channels
            raw.copy().pick(original_bads).compute_psd().plot(title='original bad channels')
        add_input = input("Add user channels to bad channels? (y/n)")
        if add_input == 'y':
            raw.info['bads'].extend(bad_sensors)
            if plot_bads:
                raw.copy().pick(original_bads + bad_sensors).compute_psd().plot(title='all bad channels')
    else:
        print("No bad channels added by user")
        if plot_bads:
            raw.copy().pick(original_bads).compute_psd().plot()

    return bad_sensors


# fill these out
deriv_suffix = 'raw_sss'
head_pos_suffix = 'head_pos'  # name for headposition file

bids_path = BIDSPath(subject=config.session_info.subject, 
                     session=config.session_info.session, 
                     task=config.session_info.task, 
                     run=config.session_info.run, 
                     datatype=config.session_info.datatype,
                     suffix=config.session_info.meg_suffix, 
                     extension=config.session_info.extension,
                     root=config.directories.bids_root)


deriv_fname = bids_path.basename.replace(config.session_info.meg_suffix, deriv_suffix) 
head_pos_fname = deriv_fname.replace(deriv_suffix, head_pos_suffix)

# Read raw data 
if config.session_info.task == 'rest': 
    if config.session_info.run == '02':
        bids_path2 = bids_path.copy().update(run='02')
        if op.exists(bids_path2):    
            raw1 = read_raw_bids(bids_path=bids_path, 
                                    extra_params={'preload':True},
                                    verbose=True)  #'fif files will be read with allow_maxshield=True by default'                          
            raw2 = read_raw_bids(bids_path=bids_path2, 
                                    extra_params={'preload':True},
                                    verbose=True)
            raw2.info['dev_head_t'] = raw1.info['dev_head_t']  # to solve the error about head position not being aligned
            raw = mne.io.concatenate_raws([raw1, raw2])
        else:
            raw = read_raw_bids(bids_path=bids_path, 
                                extra_params={'preload': True}, 
                                verbose=True)
else:  # if = run != 02 or if = task != rest
    raw = read_raw_bids(bids_path=bids_path, 
                        extra_params={'preload':True},
                        verbose=True)

# Identify and show faulty sensors using max filtering 
"""to identify bad channels it is best to use concatenated files (in case of
multiple meg files) and then run the maxfilter for files separately (works
better on separate files) 
"""
auto_noisy_chs, auto_flat_chs, auto_scores = preproc.find_bad_channels_maxwell(
                                                raw.copy(), 
                                                cross_talk=bids_path.meg_crosstalk_fpath, 
                                                calibration=bids_path.meg_calibration_fpath,
                                                return_scores=True, 
                                                verbose=True)

# Set noisy and flat channels as 'bads' in the data set then get user marked bad channels
raw.info["bads"] = auto_noisy_chs + auto_flat_chs
original_bads = deepcopy(raw.info["bads"])
user_bads = get_bad_sensors_from_user(original_bads, raw)

# Fix MEGIN magnetometer coil types (type 3022 and 3023 to 3024) for compatibility across systems
raw.fix_mag_coil_types()

# Apply the Maxfilter with fine calibration and cross-talk reduction (SSS)
coord_frame = 'meg'  # set coordinate frame    
raw_sss = preproc.maxwell_filter(raw, 
                                 cross_talk=bids_path.meg_crosstalk_fpath,
                                 calibration=bids_path.meg_calibration_fpath, 
                                 st_duration=st_duration,
                                 origin='auto',
                                 coord_frame=coord_frame, 
                                 verbose=True)

# Plot head position during each run using cHPI info
chpi_freqs, ch_idx, chpi_codes = mne.chpi.get_chpi_info(info=raw.info)
print(f"cHPI coil frequencies extracted from raw: {chpi_freqs} Hz")

# Compute head position from the coil locations
"""
These head positions can then be used with mne.preprocessing.maxwell_filter()
to compensate for movement, or with mne.preprocessing.annotate_movement() to
mark segments as bad that deviate too much from the average head position.
"""
chpi_amplitudes = mne.chpi.compute_chpi_amplitudes(raw)  # get amplitude of cHPI
chpi_locs = mne.chpi.compute_chpi_locs(raw.info, chpi_amplitudes)  # compute time-varying HPI coil locations from amplitudes
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

# Remove cHPI frequencies and save sss/tsss file
raw_sss_filtered = raw_sss.copy().filter(0.3,100)  
raw_sss_filtered.save(deriv_fname, overwrite=True)

print("Reporting output of P02_apply_maxfilter_config")
html_report_fname = op.join(session_info.report_folder, 
                            f'report_{session_info.subject}_{session_info.session}_{session_info.task}_raw_sss.html')
report_html = mne.Report(title=f'sub-{session_info.subject}_{session_info.task}')
raw.filter(0.3,100)  # filter raw data to become similar to sss for the report
report_html.add_raw(raw=raw, 
                title='Raw <60Hz', 
                psd=True, 
                butterfly=False, 
                tags=('raw'))
report_html.add_raw(raw=raw_sss_filtered, 
                title='Max filter (sss) <60Hz', 
                psd=True, 
                butterfly=False, 
                tags=('MaxFilter'))
# Plot head movement
fig, axs = plt.subplots(figsize=(10, 6))
mne.viz.plot_head_positions(head_pos, 
                            mode="traces", 
                            show=False)
plt.annotate(f'Average movement: {head_pos_avg_cmbnd_three_planes:.2f}', 
             xy=(0.1, 0.2), 
             xycoords='axes fraction')
plt.annotate(f'Std deviation of movement: {head_pos_std_cmbnd_three_planes:.2f}', 
             xy=(0.1, 0.05), 
             xycoords='axes fraction')
fig_head_pos = plt.gcf()
report_html.add_figure(fig_head_pos, 
                    title="head position over time",
                    tags=('cHPI'), 
                    image_format="PNG")

report_html.save(html_report_fname, 
            overwrite=True, 
            open_browser=True)  

full_report_input = input("Do you want to add this to the full report (without head position) (y/n)? ")
if full_report_input == 'y':
    report = mne.Report(title=f'Sub-{session_info.subject}_{session_info.task}')
    raw.filter(0.3,100)  # filter raw data to become similar to sss for the report
    report.add_raw(raw=raw, 
                    title='Raw <60Hz', 
                    psd=True, 
                    butterfly=False, 
                    tags=('raw'))
    report.add_raw(raw=raw_sss_filtered, 
                    title='Max filter (sss) <60Hz', 
                    psd=True, 
                    butterfly=False, 
                    tags=('MaxFilter'))
    report.save(session_info.report_fname, 
                overwrite=True)

























