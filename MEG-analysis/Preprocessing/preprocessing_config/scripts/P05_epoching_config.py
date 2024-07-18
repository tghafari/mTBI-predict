# -*- coding: utf-8 -*-
"""
===============================================
08. Epoching raw data based on conditions

This code will epoch continuous MEG signal based
on conditions saved in stim channel and generates 
an HTML report about epochs.

THIS SCRIPT ONLY WORKS ON SPATIAL ATTENTION
NOW.

written by Tara Ghafari
adapted from flux pipeline
==============================================
"""

import os.path as op
import os
import sys
import argparse

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from autoreject import get_rejection_threshold

import mne
from mne_bids import BIDSPath, read_raw_bids

# Add the project root directory to the sys.path
project_root = op.abspath(op.join(op.dirname(__file__), '..'))
config_root = op.join(project_root, 'config')
sys.path.append(config_root)

from config import Config

def read_raw_data(bids_path, input_fpath):
    """Read raw data using BIDS path and input file name."""
    raw = read_raw_bids(bids_path=bids_path, verbose=False, extra_params={'preload': True})
    events, events_id = mne.events_from_annotations(raw, event_id='auto')
    raw_ica = mne.io.read_raw_fif(input_fpath, allow_maxshield=True, verbose=True, preload=True)

    return raw_ica, events, events_id

def create_epochs(raw_ica, events, events_id, epo_tmin, epo_tmax):
    """Create epochs from raw ICA data."""
    return mne.Epochs(
        raw_ica, 
        events, 
        events_id,   
        tmin=epo_tmin, 
        tmax=epo_tmax,
        baseline=None, 
        proj=True, 
        picks='all', 
        detrend=1, 
        event_repeated='merge',
        reject=None, 
        reject_by_annotation=True,
        preload=True, 
        verbose=True
    )

def reject_bad_epochs(epochs):
    """Reject bad epochs based on peak-to-peak magnitude. """
    reject = get_rejection_threshold(epochs, ch_types=['mag', 'grad'], decim=10)
    print(f"\n\n Number of epochs BEFORE rejection: {len(epochs.events)} \n\n")
    epochs.drop_bad(reject=reject)
    print(f"\n\n Number of epochs AFTER rejection: {len(epochs.events)} \n\n")
    return epochs

def save_epochs(epochs, deriv_fname):
    """Save the epoched data."""
    fig_bads = epochs.plot_drop_log()
    epochs.save(deriv_fname, overwrite=True)
    return fig_bads

def create_plot_evoked_data(epochs, test_plot):
    """
    Plot evoked responses for testing.
    Create evoked data for conditions of interest and generate plots.
    """
    if test_plot:
        evoked_obj_topo_plot = [
        epochs['cue_onset_left'].average(picks=['grad']), 
        epochs['cue_onset_right'].average(picks=['grad'])
        ]
        fig_epocheds = mne.viz.plot_evoked_topo(evoked_obj_topo_plot, show=False)
    else:
        fig_epocheds = None

    evoked = epochs['cue_onset_right', 'cue_onset_left'].copy().average(method='mean').filter(0.0, 60).crop(-.2, .8)
    topos_times = np.arange(50, 450, 30) * 0.001
    fig_mag = evoked.copy().pick('mag').plot_joint(times=topos_times, show=False)
    fig_grad = evoked.copy().pick('grad').plot_joint(times=topos_times, topomap_args={'vlim': (0, 140)}, show=False)
    return  fig_epocheds, fig_mag, fig_grad

def create_report(subject, session, task, report_folder, report_fname, fig_bads, fig_mag, fig_grad, fig_epocheds=None):
    """
    Generate an HTML report with the figures.
    """
    html_report_fname = op.join(report_folder, f'report_{subject}_{session}_{task}_epo.html')
    report_html = mne.Report(title=f'sub-{subject}_{task}')

    if fig_epocheds:
        report_html.add_figure(fig=fig_epocheds, title='Evoked Topo', caption='Avg right and left cue epochs', tags=('epo'), section='Epoched')
    
    report_html.add_figure(fig=fig_bads, title='Dropped Epochs', caption='Epochs dropped from each sensor', tags=('epo'), section='Epoched')
    report_html.add_figure(fig=fig_mag, title='Evoked Magnetometer', caption='Evoked response for cue = 0-200ms', tags=('evo'), section='Evoked')
    report_html.add_figure(fig=fig_grad, title='Evoked Gradiometer', caption='Evoked response for cue = 0-200ms', tags=('evo'), section='Evoked')
    report_html.save(html_report_fname, overwrite=True, open_browser=True)

    full_report_input = input("Do you want to add this to the full report (except the evoked topo plot)(y/n)? ")
    if full_report_input.lower() == 'y':
        report = mne.open_report(report_fname)
        report.add_figure(fig=fig_bads, title='Dropped Epochs', caption='Epochs dropped from each sensor', tags=('epo'), section='Epoched')
        report.add_figure(fig=fig_mag, title='Evoked Magnetometer', caption='Evoked response for cue = 0-200ms', tags=('evo'), section='Evoked')
        report.add_figure(fig=fig_grad, title='Evoked Gradiometer', caption='Evoked response for cue = 0-200ms', tags=('evo'), section='Evoked')
        report.save(report_fname, overwrite=True)

        # Save the full preprocessing report in html and open
        full_html_report_fname = op.join(report_folder, f'report_{subject}_{session}_{task}_full.html')
        report.save(full_html_report_fname, overwrite=True, open_browser=True)


def main(subject, session):
    # Initialize the config
    config = Config(site='Birmingham', subject=subject, session=session, task='SpAtt')

    test_plot = True  # set to True if you want to plot evoked responses topographically- sanity check

    bids_path, input_fpath, deriv_fpath = config.directories.get_bids_paths(input_suffix='ica', deriv_suffix='epo')

    raw_ica, events, events_id = read_raw_data(bids_path, input_fpath)
    epochs = create_epochs(raw_ica, events, events_id, config.epoch_params.epo_tmin, config.epoch_params.epo_tmax)
    epochs = reject_bad_epochs(epochs)
    fig_bads = save_epochs(epochs, deriv_fpath)
    
    fig_epocheds, fig_mag, fig_grad = create_plot_evoked_data(epochs, test_plot)
    create_report(config.session_info.subject, config.session_info.session,
                config.session_info.task, config.directories.report_folder,
                config.directories.report_fname, fig_bads, fig_mag, fig_grad, 
                fig_epocheds)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Epoching")
    parser.add_argument('--subject', type=str, required=True, help='Subject ID')
    parser.add_argument('--session', type=str, required=True, help='Session ID')
    
    args = parser.parse_args()
    main(args.subject, args.session)