# -*- coding: utf-8 -*-
"""
===============================================
P02. Applying MaxFilter_config

This code uses MaxFilter to reduce artifacts from
environmental sources and sensor noise. 
This is part of the automated preprocessing
pipeline.

written by Tara Ghafari
adapted from oscfer88
==============================================
"""

import os
import os.path as op
import sys

import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
import argparse

import mne
from mne_bids import BIDSPath, read_raw_bids
import mne.preprocessing as preproc

# Add the project root directory to the sys.path
project_root = op.abspath(op.join(op.dirname(__file__), '..'))
config_root = op.join(project_root, 'config')
sys.path.append(config_root)

from config import Config

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
    maxwell (eg. MEG1323) or press d to finish:")  # removed indent to ensure continuity when printing on terminal
        if user_bads.lower() == 'd':
            break
        bad_sensors.append(user_bads)
    
    if bad_sensors:
        if plot_bads:
            fig_user = raw.copy().pick(bad_sensors).compute_psd(fmin=0.1, fmax=100).plot()  # double check bad channels
            fig_user.suptitle('User added bad channels')
            fig_orig = raw.copy().pick(original_bads).compute_psd(fmin=0.1, fmax=100).plot()
            fig_orig.suptitle('Original bad channels')
        add_input = input("Add user channels to bad channels? (y/n)")
        if add_input == 'y':
            raw.info['bads'].extend(bad_sensors)
            if plot_bads:
                fig_all = raw.copy().pick(original_bads + bad_sensors).compute_psd(fmin=0.1, fmax=100).plot()
                fig_all.suptitle('All bad channels')
    else:
        print("No bad channels added by user")
        if plot_bads:
            raw.copy().pick(original_bads).compute_psd(fmin=0.1, fmax=100).plot()
    
    return bad_sensors

def read_and_concatenate_raw_data(config, bids_path):
    """
    Read and concatenate raw data.
    It only does so if it is resting state and has 2 runs.
    """
    
    if config.session_info.task == 'rest' and config.session_info.run == '02':
        bids_path2 = bids_path.copy().update(run='02')
        if op.exists(bids_path2):
            raw1 = read_raw_bids(bids_path=bids_path, extra_params={'preload': True}, verbose=True)
            raw2 = read_raw_bids(bids_path=bids_path2, extra_params={'preload': True}, verbose=True)
            raw2.info['dev_head_t'] = raw1.info['dev_head_t']
            raw = mne.io.concatenate_raws([raw1, raw2])
        else:
            raw = read_raw_bids(bids_path=bids_path, extra_params={'preload': True}, verbose=True)
    else:
        raw = read_raw_bids(bids_path=bids_path, extra_params={'preload': True}, verbose=True)
    
    return raw

def apply_maxwell_filter(raw, bids_path, st_duration):
    """Apply Maxwell filter with fine calibration and cross-talk reduction."""
    return preproc.maxwell_filter(raw, 
                                  cross_talk=bids_path.meg_crosstalk_fpath,
                                  calibration=bids_path.meg_calibration_fpath, 
                                  st_duration=st_duration,
                                  origin='auto',
                                  coord_frame='meg', 
                                  verbose=True)

def compute_and_save_head_pos(raw, head_pos_fpath):
    """
    These head positions can then be used with mne.preprocessing.maxwell_filter()
    to compensate for movement, or with mne.preprocessing.annotate_movement() to
    mark segments as bad that deviate too much from the average head position.
    """

    chpi_amplitudes = mne.chpi.compute_chpi_amplitudes(raw)
    chpi_locs = mne.chpi.compute_chpi_locs(raw.info, chpi_amplitudes)
    head_pos = mne.chpi.compute_head_pos(raw.info, chpi_locs, verbose=True)
    mne.chpi.write_head_pos(head_pos_fpath, head_pos)
    
    return head_pos

def compute_head_pos_stats(head_pos):
    """ 
    Average across all timepoints for x, y, and z
    which are head_pos[:,4:7]. then calculate the combined
    movement in three axes and average and std
    """
    head_pos_avg_three_planes = np.mean(head_pos[:, 4:7], axis=0)
    head_pos_std_three_planes = np.std(head_pos[:, 4:7], axis=0)
    head_pos_avg_cmbnd_three_planes = np.sqrt(np.sum(head_pos_avg_three_planes**2))
    head_pos_std_cmbnd_three_planes = np.sqrt(np.sum(head_pos_std_three_planes**2))
    
    return head_pos_avg_cmbnd_three_planes, head_pos_std_cmbnd_three_planes

def create_report(subject, session, task, report_folder, report_fname, raw, raw_sss_filtered, head_pos, head_pos_avg, head_pos_std):
    """Create and save the MNE report."""

    html_report_fname = op.join(report_folder, f'report_{subject}_{session}_{task}_raw_sss.html')
    report_html = mne.Report(title=f'Sub-{subject}_{task}')
    
    raw.filter(0.3, 100)
    report_html.add_raw(raw=raw, title='Raw <60Hz', psd=True, butterfly=False, tags=('raw'))
    report_html.add_raw(raw=raw_sss_filtered, title='Max filter (sss) <60Hz', psd=True, butterfly=False, tags=('MaxFilter'))
    
    fig, axs = plt.subplots(figsize=(10, 6))
    mne.viz.plot_head_positions(head_pos, mode="traces", show=False)
    plt.annotate(f'Average movement: {head_pos_avg:.2f}', xy=(0.1, 0.2), xycoords='axes fraction')
    plt.annotate(f'Std deviation of movement: {head_pos_std:.2f}', xy=(0.1, 0.05), xycoords='axes fraction')
    fig_head_pos = plt.gcf()
    report_html.add_figure(fig_head_pos, title="Head position over time", tags=('cHPI'), image_format="PNG")
    
    report_html.save(html_report_fname, overwrite=True, open_browser=True)

    full_report_input = input("Do you want to add this to the full report (without head position) (y/n)? ")
    if full_report_input.lower() == 'y':
        full_report = mne.Report(title=f'Sub-{subject}_{task}')
        raw.filter(0.3, 100)
        full_report.add_raw(raw=raw, title='Raw <60Hz', psd=True, butterfly=False, tags=('raw'))
        full_report.add_raw(raw=raw_sss_filtered, title='Max filter (sss) <60Hz', psd=True, butterfly=False, tags=('MaxFilter'))
        full_report.save(report_fname, overwrite=True)

def main(subject, session):
    # Initialize the config
    config = Config(site='Birmingham', subject=subject, session=session, task='SpAtt')

    deriv_suffix = 'raw_sss'
    head_pos_suffix = 'head_pos'
    
    bids_path, _, deriv_fpath = config.directories.get_bids_paths(input_suffix='raw_sss', deriv_suffix='raw_sss')

    head_pos_fpath = deriv_fpath.replace(deriv_suffix, head_pos_suffix)
    
    raw = read_and_concatenate_raw_data(config, bids_path)  # this only extecutes if we have run=02 and task='rest'
    
    # Identify and show faulty sensors using max filtering 
    """
    to identify bad channels it is best to use concatenated files (in case of
    multiple meg files) and then run the maxfilter for files separately (works
    better on separate files) 
    """
    auto_noisy_chs, auto_flat_chs, _ = preproc.find_bad_channels_maxwell(
        raw.copy(), 
        cross_talk=bids_path.meg_crosstalk_fpath, 
        calibration=bids_path.meg_calibration_fpath,
        return_scores=True, 
        verbose=True)
    
    # Set noisy and flat channels as 'bads' in the data set then get user marked bad channels
    raw.info["bads"] = auto_noisy_chs + auto_flat_chs
    original_bads = deepcopy(raw.info["bads"])
    _ = get_bad_sensors_from_user(original_bads, raw)
    
    # Fix MEGIN magnetometer coil types (type 3022 and 3023 to 3024) for compatibility across systems
    raw.fix_mag_coil_types()
    
    raw_sss = apply_maxwell_filter(raw, bids_path, config.st_duration)
    head_pos = compute_and_save_head_pos(raw, head_pos_fpath)    
    head_pos_avg, head_pos_std = compute_head_pos_stats(head_pos)

    # Remove cHPI frequencies and save sss/tsss file
    raw_sss_filtered = raw_sss.copy().filter(0.3, 100)
    raw_sss_filtered.save(deriv_fpath, overwrite=True)
    
    create_report(config.session_info.subject, config.session_info.session,
                  config.session_info.task, config.directories.report_folder,
                  config.directories.report_fname, raw, raw_sss_filtered, 
                  head_pos, head_pos_avg, head_pos_std)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run maxfilter")
    parser.add_argument('--subject', type=str, required=True, help='Subject ID')
    parser.add_argument('--session', type=str, required=True, help='Session ID')
    
    args = parser.parse_args()
    main(args.subject, args.session)