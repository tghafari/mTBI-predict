# -*- coding: utf-8 -*-
"""
===============================================
08. Epoching raw data based on conditions

This code will epoch continuous MEG signal based
on conditions saved in stim channel and generates 
an HTML report about epochs.

written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:
    1) which epochs to keep?
    
Issues/ contributions to community:

    
Questions:


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
config = Config()

# fill these out
input_suffix = 'ica'
deriv_suffix = 'epo'
test_plot = False  # set to True if you want to plot the data for testing

# Specify specific file names
bids_path = BIDSPath(subject=config.session_info.subject, 
                     session=config.session_info.session, 
                     task=config.session_info.task, 
                     run=config.session_info.run, 
                     datatype=config.session_info.datatype,
                     suffix=config.session_info.meg_suffix, 
                     extension=config.session_info.extension,
                     root=config.directories.bids_root)

bids_fname = bids_path.basename.replace(config.directories.meg_suffix, input_suffix)  # only used for suffices that are not recognizable to bids 
input_fname = op.join(config.directories.deriv_folder, bids_fname)
deriv_fname = str(input_fname).replace(input_suffix, deriv_suffix)



summary_rprt = True  # do you want to add evokeds figures to the summary report?
test_plot = False  # do you want to plot the data to test (True) or just generate report (False)?



raw = read_raw_bids(bids_path=bids_path, 
                    verbose=False, 
                    extra_params={'preload':True})  # read raw for events and event ids only

events, events_id = mne.events_from_annotations(raw, event_id='auto')

# read raw and events file
raw_ica = mne.io.read_raw_fif(input_fname, allow_maxshield=True,
                              verbose=True, preload=True)


epochs = mne.Epochs(raw_ica, 
                    events, 
                    events_id,   # select events_picks and events_picks_id                   
                    tmin=config.epoch_info.tmin, 
                    tmax=config.epoch_info.tmax,
                    baseline=None, 
                    proj=True, 
                    picks='all', 
                    detrend=1, 
                    event_repeated='merge',
                    reject=None,  # we'll reject after calculating the threshold
                    reject_by_annotation=True,
                    preload=True, 
                    verbose=True)

# Set the peak-peak amplitude threshold for trial rejection.
""" subject to change based on data quality
can be automatically detected: second option"""
reject = get_rejection_threshold(epochs, 
                                 ch_types=['mag', 'grad'],
                                 decim=10)

# Drop bad epochs based on peak-to-peak magnitude
print(f"\n\n Numer of epochs BEFORE rejection: {len(epochs.events)} \n\n")
epochs.drop_bad(reject=reject)
print(f"\n\n Numer of epochs AFTER rejection: {len(epochs.events)} \n\n")

# Save the epoched data 
fig_bads = epochs.plot_drop_log()  # rejected epochs
epochs.save(deriv_fname, overwrite=True)

if test_plot:
    # Topo plot evoked responses
    evoked_obj_topo_plot = [epochs['cue_onset_left'].average(picks=['grad']), epochs['cue_onset_right'].average(picks=['grad'])]
    fig_epocheds = mne.viz.plot_evoked_topo(evoked_obj_topo_plot, show=True)

print("Reporting output of P05_epoching_config")
html_report_fname = op.join(config.session_info.report_folder, 
                            f'report_{config.session_info.subject}_{config.session_info.session}_{config.session_info.task}_epo.html')
report_html = mne.Report(title=f'sub-{config.session_info.subject}_{config.session_info.task}')

report_html.add_figure(fig=fig_epocheds, 
                title='evoked topo',
                caption='avg right and left cue epochs', 
                tags=('epo'),
                section='epocheds'
                )
report_html.add_figure(fig=fig_bads, 
                title='dropped epochs',
                caption='epochs dropped from each sensor', 
                tags=('epo'),
                section='epocheds'
                )
report_html.save(html_report_fname, overwrite=True, open_browser=True)  # to check how the report looks


full_report_input = input("Do you want to add this to the full report (y/n)? ")
if full_report_input == 'y':
    report = mne.open_report(config.directories.report_fname)

    report.add_figure(fig=fig_bads, 
                    title='dropped epochs',
                    caption='epochs dropped from each sensor', 
                    tags=('epo'),
                    section='epocheds'
                    )

    report.save(config.directories.report_fname, overwrite=True)
