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

import mne
from mne_bids import BIDSPath, read_raw_bids

# fill these out
site = 'Birmingham'
subject = '2002'  # subject code in mTBI project
session = '04B'  # data collection session within each run
run = '01'  # data collection run for each participant
task = 'SpAtt'
meg_extension = '.fif'
meg_suffix = 'meg'
input_suffix = 'ica'
deriv_suffix = 'epo'

using_events_csv = False  # for when we are not using events_from_annotation. default is False
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
bids_root = op.join(mTBI_root, 'collected-data', 'BIDS', 'task_BIDS')  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, 
                     suffix=meg_suffix, extension=meg_extension)

raw = read_raw_bids(bids_path=bids_path, verbose=False, 
                     extra_params={'preload':True})  # read raw for events and event ids only

deriv_folder = op.join(bids_root, 'derivatives', 'sub-' + subject, 
                       'task-' + task)  # RDS folder for results
bids_fname = bids_path.basename.replace(meg_suffix, input_suffix)  # only used for suffices that are not recognizable to bids 
input_fname = op.join(deriv_folder, bids_fname)
deriv_fname = str(input_fname).replace(input_suffix, deriv_suffix)


# read raw and events file
raw_ica = mne.io.read_raw_fif(input_fname, allow_maxshield=True,
                              verbose=True, preload=True)

if using_events_csv:
    event_fname = op.join(bids_path.directory, 'meg',
                          bids_path.basename.replace('meg.fif', 'events.tsv'))
    events_file = pd.read_csv(event_fname, sep='\t')
    
    # Some variable preparation in case we are using bids events file instead of mne
    events = events_file[['sample','duration','value']].to_numpy(dtype=int)
    events[:,0] = events[:,0] + raw_ica.first_samp  # begin from the first sample
    event_to_series = events_file.copy().drop_duplicates(subset='trial_type')[['value','trial_type']]
    events_id = pd.Series(event_to_series['value'].values, index=event_to_series['trial_type']).to_dict()
    events_color = {'cue_onset_right':'red', 'cue_onset_left':'blue'}
    
    # creates a variable like mne.pick_events
    events_picks = np.vstack(((events[events[:,2]==102]), (events[events[:,2]==101])))
    events_picks[events_picks[:,0].argsort()]
    events_picks_id = {k:v for k, v in events_id.items() if k.startswith('cue onset')}  # select only epochs you are interested in
    
    # Take a quick look at the events file
    plt.figure()
    plt.stem(events_file['onset'], events_file['trial_type'])
    plt.xlim(0,200)  # only show first 200 seconds
    plt.xlabel('time (sec)')
    plt.ylabel('event type')
    plt.show()

else:
    events, events_id = mne.events_from_annotations(raw, event_id='auto')

# just for oscar's
# raw_list = list()
# events_list = list()
# events_list.append(events)
# raw_ica, events = mne.concatenate_raws(raw_list, preload=True,
#                                         events_list=events_list)
# end of oscar's

# Set the peak-peak amplitude threshold for trial rejection.
""" subject to change based on data quality"""
reject = dict(grad=5000e-13,  # T/m (gradiometers)
              mag=5e-12,      # T (magnetometers)
              #eog=150e-6      # V (EOG channels)
              )

# Make epochs (2 seconds centered on stim onset)
metadata, _, _ = mne.epochs.make_metadata(
                events=events, event_id=events_id, 
                tmin=-1.5, tmax=1, 
                sfreq=raw_ica.info['sfreq'])

epochs = mne.Epochs(raw_ica, events, events_id,   # select events_picks and events_picks_id                   
                    metadata=metadata,            # if only interested in specific events (not all)
                    tmin=-0.8, tmax=1.2,
                    baseline=None, proj=True, picks='all', 
                    detrend=1, event_repeated='drop',
                    reject=reject, reject_by_annotation=True,
                    preload=True, verbose=True)

# Defie epochs we care about
conds_we_care_about = ["cue_onset_right", "cue_onset_left", "stim_onset", "response_press_onset"] # TODO:discuss with Ole
epochs.equalize_event_counts(conds_we_care_about)  # this operates in-place

# Save the epoched data 
epochs.save(deriv_fname, overwrite=True)

############################### Check-up plots ################################
# Plotting to check the raw epoch
epochs['cue_onset_left'].plot(events=events, event_id=events_id, n_epochs=10)  # shows all the events in the epoched data that's based on 'cue_onset_left'
epochs['cue_onset_right'].plot(events=events, event_id=events_id, n_epochs=10) 

# plot amplitude on heads
times_to_topomap = [-.1, .1, .8, 1.1]
epochs['cue_onset_left'].average(picks=['meg']).plot_topomap(times_to_topomap)  # title='cue onset left (0 sec)'
epochs['cue_onset_right'].average(picks=['meg']).plot_topomap(times_to_topomap)  # title='cue onset right (0 sec)'

# Topo plot evoked responses
evoked_obj_topo_plot = [epochs['cue_onset_left'].average(picks=['grad']), epochs['cue_onset_right'].average(picks=['grad'])]
mne.viz.plot_evoked_topo(evoked_obj_topo_plot, show=True)

fig_bads = epochs.plot_drop_log()  # rejected epochs
###############################################################################

# Plots the average of one epoch type - pick best sensors for report
epochs['cue_onset_left'].average(picks=['meg']).copy().filter(1,60).plot()
epochs['cue_onset_right'].average(picks=['meg']).copy().filter(1,60).plot()

# Plots to save
fig_right = epochs['cue_onset_right'].copy().filter(0.0,30).crop(-.1,1.2).plot_image(
    picks=['MEG1932'],vmin=-100,vmax=100)  # event related field image
fig_left = epochs['cue_onset_left'].copy().filter(0.0,30).crop(-.1,1.2).plot_image(
    picks=['MEG2332'],vmin=-100,vmax=100)  # event related field image

if summary_rprt:
    report_root = op.join(mTBI_root, r'results-outputs/mne-reports')  # RDS folder for reports
    
    if not op.exists(op.join(report_root , 'sub-' + subject, 'task-' + task)):
        os.makedirs(op.join(report_root , 'sub-' + subject, 'task-' + task))
    report_folder = op.join(report_root , 'sub-' + subject, 'task-' + task)

    report_fname = op.join(report_folder, 
        f'mneReport_sub-{subject}_{task}_1.hdf5')    # it is in .hdf5 for later adding images
    html_report_fname = op.join(report_folder, f'report_preproc_{task}_1.html')

    report = mne.open_report(report_fname)

    report.add_figure(fig=fig_right, title='cue right',
                    caption='evoked response on one left sensor (MEG1943)', 
                    tags=('epo'),
                    section='epocheds'
                    )
    report.add_figure(fig=fig_left, title='cue left',
                    caption='evoked response on one right sensor (MEG2522)', 
                    tags=('epo'),
                    section='epocheds' 
                    )   
    report.save(report_fname, overwrite=True, open_browser=True)
    report.save(html_report_fname, overwrite=True, open_browser=True)  # to check how the report looks
