# -*- coding: utf-8 -*-
"""
===========
Config file
===========

Configurate the parameters of the mTBI-predict study.

"""


import os
import os.path as op
import pandas as pd



class Config:
    def __init__(self, site, subject, session, run, task, datatype, suffix, extension, platform):
        self.site = site
        self.subject = subject
        self.session = session
        self.run = run
        self.task = task
        self.datatype = datatype
        self.suffix = suffix
        self.extension = extension
        self.platform = platform
        self.set_directories()

    
    def set_directories(self):  # change these directories according to your system
        if self.platform == 'bluebear':
            self.rds_dir = '/rds/projects/j/jenseno-avtemporal-attention'
            self.camcan_dir = '/rds/projects/q/quinna-camcan/dataman/data_information'
        elif self.platform == 'windows':
            self.rds_dir = 'Z:'
            self.camcan_dir = 'X:/dataman/data_information'
        elif self.platform == 'mac':
            self.rds_dir = '/Volumes/jenseno-avtemporal-attention'
            self.camcan_dir = '/Volumes/quinna-camcan/dataman/data_information'
        else:
            raise ValueError("Invalid platform. Choose 'bluebear', 'mac', or 'windows'.")

        self.mTBI_root = op.join(self.rds_dir, 'Projects/mTBI-predict')
        self.bids_root = op.join(self.mTBI_root, 'collected-data', 'BIDS', 'task_BIDS')
        self.deriv_root = op.join(self.bids_root, 'derivatives')
        
        self.deriv_folder = op.join(self.deriv_root, f'sub-{self.subject}', f'task-{self.task}')
        if not op.exists(self.deriv_folder):
            os.makedirs(self.deriv_folder)

# =============================================================================
# SESSION-SPECIFIC SETTINGS 
# =============================================================================
# Create an instance of the class for each subject
session_info = Config(site='Birmingham', 
                      subject='2013', 
                      session='02B', 
                      run='01', 
                      task='SpAtt',
                      datatype ='meg',
                      suffix='meg', 
                      extension='.fif')

# =============================================================================
# PATH & BIDS SETTINGS
# =============================================================================
# Define the platform to set directories
directories = Config(platform='mac')

# =============================================================================
# MAXWELL FILTERING SETTINGS
# =============================================================================

# Apply Spatiotemporal SSS (tsss) by passing st_duration to maxwell_filter

method = 'sss'  # set filtering method (sss/tsss)
if method == 'tsss':
    st_duration = 10
else:
    st_duration = None

# =============================================================================
# ARTIFACT ANNOTATION SETTINGS
# =============================================================================

# Set muscle artifact threshold (z-scores)
# IMPORTTANT: This threshold is data dependent, check the optimal threshold by 
# plotting "scores_muscle"
threshold_muscle = 7


# =============================================================================
# ICA SETTINGS
# =============================================================================

ica_method = 'fastica'
n_components = 0.99
max_iter = 800
random_state = 1688

# Rejected ICs (manually selected)  #TODO: to be changed
rej_ic = pd.DataFrame({
    'sub': ['SA113','SA116','SA118','SA124','SA126','SA127'],
    'meg_ica_eog': [[4],[2],[3],[14],[8],[3]],
    'meg_ica_ecg': [[7],[5,18],[5],[16],[7],[4]],
    'eeg_ica_eog': [[2,7],[],[],[],[],[]],
    'eeg_ica_ecg': [[],[],[],[],[],[]]})


# =============================================================================
# EPOCHING SETTINGS
# =============================================================================

# Set timewindow
tmin = -1
tmax = 2.5

# Epoch rejection criteria
reject = dict(grad=4000e-13,    # T / m (gradiometers)
                      mag=4e-12,        # T (magnetometers)
                      eeg=200e-6       # V (EEG channels)
                      )
# reject = dict(grad=4000e-13,    # T / m (gradiometers)
#                   mag=4e-12         # T (magnetometers)
#                   )

# Set epoching event ids
if visit_id == 'V1':
    events_id = {}
    types = ['face','object','letter','false']
    for j,t in enumerate(types):
        for i in range(1,21):
            events_id[t+str(i)] = i + j * 20
elif visit_id == 'V2':
    events_id = {}
    events_id['blank'] = 50
    types = ['face','object']
    for j,t in enumerate(types):
        for i in range(1,11):
            events_id[t+str(i)] = i + j * 20


# =============================================================================
#  FACTOR AND CONDITIONS OF INTEREST
# =============================================================================

if visit_id == 'V1':
    # factor = ['Category']
    # conditions = ['face', 'object', 'letter', 'false']
    
    # factor = ['Duration']
    # conditions = ['500ms', '1000ms', '1500ms']
    
    # factor = ['Task_relevance']
    # conditions = ['Relevant_target','Relevant_non-target','Irrelevant']
    
    factor = ['Duration', 'Task_relevance']
    conditions = [['500ms', '1000ms', '1500ms'],
                   ['Relevant target','Relevant non-target','Irrelevant']]
elif visit_id == 'V2':
    factor = ['Category']
    conditions = ['face', 'object']
    
    
# =============================================================================
# TIME-FREQUENCY REPRESENTATION SETTINGS
# =============================================================================

baseline_w = [-0.5, -0.25]     #only for plotting
freq_band = ['low', 'high']    #can be 'low', 'high' or ['low', 'high']


# =============================================================================
# SOURCE MODELING
# =============================================================================

# Forward model
spacing='oct6'  #from forward_model
space='surface'   #surface or volume

# Inverse model
#   Beamforming
beam_method = 'lcmv'  #'lcmv' or 'dics'

active_win = (0.75, 1.25)
baseline_win = (-.5, 0)

# fmin = 8#60
# fmax = 12#90


# =============================================================================
# GENERAL PLOTTING
# =============================================================================

# Subset of posterior sensors  #TOFO: update this part using mne.read_vectorview_selection
post_sens = {'grad': ['MEG1932', 'MEG1933', 'MEG2122', 'MEG2123',
                     'MEG2332', 'MEG2333', 'MEG1922', 'MEG1923',
                     'MEG2112', 'MEG2113', 'MEG2342', 'MEG2343'],
             'mag': ['MEG1931', 'MEG2121',
                     'MEG2331', 'MEG1921',
                     'MEG2111', 'MEG2341'],
             'eeg': ['EEG056', 'EEG030',
                     'EEG057', 'EEG018',
                     'EEG032', 'EEG019']}