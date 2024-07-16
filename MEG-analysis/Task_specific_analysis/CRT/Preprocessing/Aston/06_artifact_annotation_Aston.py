# -*- coding: utf-8 -*-
"""
===============================================
06. Annotation of artifacts

This code will identify artifacts and then annotate
them for later use (eg., to reject).

adapted by Alice Waitt for Aston
written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:
    1) rename eog and ecg channels (if wrong names)
    2) run maxfilter on anonymized data before 
    reading them here
    
Issues:
    1) many of the blinks are not identified by find_eog_events
    2) there is no ecg or veog channgel for sub=03
    3) 

Contributions to community:
    1) read-Raw-bids doesn't work on the derivatives
    folder -> using mne_io_read_raw_fif instead
    2) get_bids_path_from_fname cannot recognize
    bids root from sss file
    3) BIDSPath doesn't read sss as suffix
    
Questions:
    1) why blink_onsets has -0.25?
    2) what exactly is raw.first_time?

"""
#%%
import os.path as op
import numpy as np
import matplotlib.pyplot as plt

import mne
from mne.preprocessing import annotate_muscle_zscore
from mne_bids import BIDSPath

# fill these out
site = 'Aston'
subject = '2001'  # subject code in mTBI project
session = '04A'  # data collection session within each run
run = '01'  # data collection run for each participant
task = 'CRT' #'rest'
meg_suffix = 'meg'
meg_extension = '.fif'
input_suffix = 'raw_sss'
deriv_suffix = 'ann'

remove_line_noise = False

platform = 'laptop' #'bluebear' # are you using 'bluebear', 'windows' or 'laptop'?
test_plot = True  # do you want to plot the data to test (True) or just generate report (False)?

#%%
# Specify specific file names
if platform == 'bluebear':
    rds_dir = r'/rds/projects/s/sidhuc-mtbi-data' #r'\\its-rds.bham.ac.uk\rdsprojects\s\sidhuc-mtbi-data' #'/rds/projects/j/jenseno-avtemporal-attention'
    data_root = op.join(rds_dir, r'Alice_Aston_testing')
    #mTBI_root = op.join(rds_dir, r'Projects/mTBI-predict')
    #data_root = op.join(mTBI_root, 'collected-data')
elif platform == 'laptop':
    rds_dir = r'C:\Users\waitta\Documents\ClusterDocs'
    data_root = op.join(rds_dir, 'BearTestSub')
#elif platform == 'windows':
#    rds_dir = 'Z:'
#    data_root = r'C:\Users\waitta\Documents\ClusterDocs\BearTestSub' #r'/clinical/vol113/raw-sub-data/'

bids_root = op.join(data_root, 'BIDS', 'task_BIDS')  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, 
                     suffix=meg_suffix, extension=meg_extension)
deriv_folder = op.join(bids_root, 'derivatives', 'sub-' + subject, 'ses-' +session, #added session
                       'task-' + task, 'run-' + run)  # RDS folder for results
bids_fname = bids_path.basename.replace(meg_suffix, input_suffix)  # only used for suffices that are not recognizable to bids 
input_fname = op.join(deriv_folder, bids_fname)
deriv_fname = str(input_fname).replace(input_suffix, deriv_suffix)

# Read max filtered data 
raw_sss = mne.io.read_raw_fif(input_fname, preload=True)  # read_raw_bids doesn't work on derivatives
# raw_sss.crop(1,6)  # crop several minutes for faster processing (for code development only)

# Remove power line noise
if remove_line_noise:
# meg_picks = mne.pick_types(raw_sss.info, meg=True)
    power_freqs = (50, 100, 150)
    raw_sss.notch_filter(freqs=power_freqs)

if test_plot:
    # Identifying and annotating eye blinks using vEOG (EOG001)
    raw_sss.copy().pick_channels(ch_names=['EOG001','EOG002'   # vEOG, hEOG, EKG
                                        ,'ECG003']).plot()  # 'plot to make sure channel' 
                                                            # 'names are correct, rename otherwise'    

#%%
# Blinks
blink_events = mne.preprocessing.find_eog_events(raw_sss, ch_name=['EOG001'])  # blinks
onset_blink = blink_events[:,0] / raw_sss.info['sfreq'] -.25 #'from flux pipline, but why?'
                                                     # 'blink onsets in seconds'
onset_blink -= raw_sss.first_time  # first_time is apparently the time start time of the raw data
n_blinks = len(blink_events)  # length of the event file is the number of blinks in total
duration_blink = np.repeat(.5, n_blinks)  # duration of each blink is assumed to be 500ms
description_blink = ['blink'] * n_blinks
annotation_blink = mne.Annotations(onset_blink, duration_blink, description_blink)

# Saccades
saccade_events = mne.preprocessing.find_eog_events(raw_sss, ch_name=['EOG002'], thresh=4e-5)#, thresh=7e-5)  # saccades
onset_saccade = saccade_events[:,0] / raw_sss.info['sfreq'] -.25 #'from flux pipline, but why?'
                                                         #'blink onsets in seconds'
onset_saccade -= raw_sss.first_time  # first_time is apparently the time start time of the raw data
n_saccades = len(saccade_events)  # length of the event file is the number of blinks in total
duration_saccade = np.repeat(.3, n_saccades)  # duration of each saccade is assumed to be 300ms
description_saccade = ['saccade'] * n_saccades
annotation_saccade = mne.Annotations(onset_saccade, duration_saccade, description_saccade)

# Muscle artifacts
""" 
muscle artifacts are identified from the magnetometer data filtered and 
z-scored in filter_freq range
"""
threshold_muscle = 10
min_length_good = .2
filter_freq = [110,140]
annotation_muscle, scores_muscle = annotate_muscle_zscore(
    raw_sss, ch_type='mag', threshold=threshold_muscle, 
    min_length_good=min_length_good, filter_freq=filter_freq)
annotation_muscle.onset -= raw_sss.first_time  # align the artifact onsets to data onset
annotation_muscle._orig_time = None  # remove date and time from the annotation variable

fig, ax = plt.subplots()
ax.plot(raw_sss.times, scores_muscle)
ax.axhline(y=threshold_muscle, color="r")
ax.set(xlabel="time, (s)", ylabel="zscore", title="Muscle activity")
plt.show()

#%%
# Include annotations in dataset and inspect
raw_sss.set_annotations(annotation_blink + annotation_saccade + annotation_muscle)
raw_sss.set_channel_types({'EOG001':'eog', 'EOG002':'eog', 'ECG003':'ecg'})  # set both vEOG and hEOG as EOG channels
eog_picks = mne.pick_types(raw_sss.info, meg=False, eog=True)
scale = dict(eog=500e-6)
raw_sss.plot(order=eog_picks, scalings=scale, start=50)

# break_annots = mne.preprocessing.annotate_break(
#    raw=raw_sss,
#    min_break_duration=20,  # consider segments of at least 20 s duration
#    t_start_after_previous=5,  # start annotation 5 s after end of previous one
#    t_stop_before_next=2,  # stop annotation 2 s before beginning of next one
#)

# Save the artifact annotated file
raw_sss.save(deriv_fname, overwrite=True)

# raw_ann = raw_sss.copy().crop_by_annotations()
# %%
