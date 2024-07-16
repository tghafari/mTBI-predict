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

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from autoreject import get_rejection_threshold

import mne
from mne_bids import BIDSPath, read_raw_bids

from config import Config

# Initialize the config
config = Config(site='Birmingham', subject='2013', session='02B', task='SpAtt')

# Configuration parameters
input_suffix = 'ica'
deriv_suffix = 'epo'
test_plot = True  # set to True if you want to plot evoked responses topographically- sanity check

def create_bids_path(config):
    """
    Create BIDS path based on the configuration.
    """
    return BIDSPath(
        subject=config.subject, 
        session=config.session, 
        task=config.task, 
        run=config.run, 
        datatype=config.datatype,
        suffix=config.meg_suffix, 
        extension=config.extension,
        root=config.directories.bids_root
    )

def create_file_paths(config, bids_path):
    """
    Create input and derivative file paths.
    """
    bids_fname = bids_path.basename.replace(config.meg_suffix, input_suffix)
    input_fname = op.join(config.directories.deriv_folder, bids_fname)
    deriv_fname = str(input_fname).replace(input_suffix, deriv_suffix)
    return input_fname, deriv_fname

def read_raw_data(bids_path, input_fname):
    """
    Read raw data using BIDS path and input file name.
    """
    raw = read_raw_bids(bids_path=bids_path, verbose=False, extra_params={'preload': True})
    events, events_id = mne.events_from_annotations(raw, event_id='auto')
    raw_ica = mne.io.read_raw_fif(input_fname, allow_maxshield=True, verbose=True, preload=True)
    return raw_ica, events, events_id

def create_epochs(raw_ica, events, events_id, config):
    """
    Create epochs from raw ICA data.
    """
    return mne.Epochs(
        raw_ica, 
        events, 
        events_id,   
        tmin=config.epoch.epo_tmin, 
        tmax=config.epoch.epo_tmax,
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
    """
    Reject bad epochs based on peak-to-peak magnitude.
    """
    reject = get_rejection_threshold(epochs, ch_types=['mag', 'grad'], decim=10)
    print(f"\n\n Number of epochs BEFORE rejection: {len(epochs.events)} \n\n")
    epochs.drop_bad(reject=reject)
    print(f"\n\n Number of epochs AFTER rejection: {len(epochs.events)} \n\n")
    return epochs

def save_epochs(epochs, deriv_fname):
    """
    Save the epoched data.
    """
    fig_bads = epochs.plot_drop_log()
    epochs.save(deriv_fname, overwrite=True)
    return fig_bads

def plot_evoked_responses(epochs):
    """
    Plot evoked responses for testing.
    """
    evoked_obj_topo_plot = [
        epochs['cue_onset_left'].average(picks=['grad']), 
        epochs['cue_onset_right'].average(picks=['grad'])
    ]
    return mne.viz.plot_evoked_topo(evoked_obj_topo_plot, show=True)

def create_evoked_data(epochs):
    """
    Create evoked data for conditions of interest and generate plots.
    """
    evoked = epochs['cue_onset_right', 'cue_onset_left'].copy().average(method='mean').filter(0.0, 60).crop(-.2, .8)
    topos_times = np.arange(50, 450, 30) * 0.001
    fig_mag = evoked.copy().pick('mag').plot_joint(times=topos_times)
    fig_grad = evoked.copy().pick('grad').plot_joint(times=topos_times, topomap_args={'vlim': (0, 140)})
    return fig_mag, fig_grad

def create_report(fig_bads, fig_mag, fig_grad, fig_epocheds=None):
    """
    Generate an HTML report with the figures.
    """
    html_report_fname = op.join(config.directories.report_folder, f'report_{config.subject}_{config.session}_{config.task}_epo.html')
    report_html = mne.Report(title=f'sub-{config.subject}_{config.task}')

    if fig_epocheds:
        report_html.add_figure(fig=fig_epocheds, title='Evoked Topo', caption='Avg right and left cue epochs', tags=('epo'), section='Epoched')
    
    report_html.add_figure(fig=fig_bads, title='Dropped Epochs', caption='Epochs dropped from each sensor', tags=('epo'), section='Epoched')
    report_html.add_figure(fig=fig_mag, title='Evoked Magnetometer', caption='Evoked response for cue = 0-200ms', tags=('evo'), section='Evoked')
    report_html.add_figure(fig=fig_grad, title='Evoked Gradiometer', caption='Evoked response for cue = 0-200ms', tags=('evo'), section='Evoked')
    report_html.save(html_report_fname, overwrite=True, open_browser=True)

    full_report_input = input("Do you want to add this to the full report (y/n)? ")
    if full_report_input.lower() == 'y':
        report = mne.open_report(config.directories.report_fname)
        report.add_figure(fig=fig_bads, title='Dropped Epochs', caption='Epochs dropped from each sensor', tags=('epo'), section='Epoched')
        report.add_figure(fig=fig_mag, title='Evoked Magnetometer', caption='Evoked response for cue = 0-200ms', tags=('evo'), section='Evoked')
        report.add_figure(fig=fig_grad, title='Evoked Gradiometer', caption='Evoked response for cue = 0-200ms', tags=('evo'), section='Evoked')
        report.save(config.directories.report_fname, overwrite=True)


def main():
    """
    Main function to run the epoching and reporting process.
    """
    bids_path = create_bids_path(config)
    input_fname, deriv_fname = create_file_paths(config, bids_path)
    raw_ica, events, events_id = read_raw_data(bids_path, input_fname)
    epochs = create_epochs(raw_ica, events, events_id, config)
    epochs = reject_bad_epochs(epochs)
    fig_bads = save_epochs(epochs, deriv_fname)
    
    if test_plot:
        fig_epocheds = plot_evoked_responses(epochs)
    else:
        fig_epocheds = None
    
    fig_mag, fig_grad = create_evoked_data(epochs)
    create_report(fig_bads, fig_mag, fig_grad, fig_epocheds)

if __name__ == "__main__":
    main()
