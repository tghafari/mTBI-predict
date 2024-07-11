# -*- coding: utf-8 -*-
"""
===========
Config file
===========

Configurate the parameters of the mTBI-predict study.

"""


import os
import pandas as pd


# =============================================================================
# SESSION-SPECIFIC SETTINGS
# =============================================================================

# experiment_id = 1
# subject_id = '109'
subject_list = ['SA124']

# Set user-specific params
user = os.getlogin()

if user in ['oscfe', 'ferranto', 'FerrantO']:               # Oscar
    site_id = 'SA'
    raw_path = r'Z:\Real_data\Exp%s'
    # raw_path = r'Z:\Real_data\Exp%s' % visit_id[1]
    # data_path = raw_path + '\%s\meg'# % site_id, subject_id
    cal_path = r'Z:\MaxFilter'
    t1_path = r'Z:\Real_data\MRI\%s'# % site_id, subject_id
    freesurfer_path = r'Z:\Real_data\MRI\%s\freesurfer'# % site_id, subject_id
elif user in ['root']:                          # Ling
    site_id = 'SB'
    raw_path = r'/Volumes/Cogitate/MEG_reorganized'
    # data_path = op.join(raw_path, site_id+subject_id,visit_id)
    cal_path = r'/Users/ling/Documents/work/Cogitate/data_analysis/Maxfilter'

# Set filename based on experiment number
if visit_id == 'V1':
    file_exts = ['%s_MEEG_V1_DurR1',
                 '%s_MEEG_V1_DurR2',
                 '%s_MEEG_V1_DurR3',
                 '%s_MEEG_V1_DurR4',
                 '%s_MEEG_V1_DurR5']
    # file_names = [f % (site_id+subject_id) for f in file_exts]
elif visit_id == 'V2':
    file_exts = ['%s_MEEG_V2_VGR1',
                 '%s_MEEG_V2_VGR2',
                 '%s_MEEG_V2_VGR3',
                 '%s_MEEG_V2_VGR4',
                 '%s_MEEG_V2_ReplayR1',
                 '%s_MEEG_V2_ReplayR2']
    # file_names = [f % (site_id+subject_id) for f in file_exts]


# =============================================================================
# GENERAL SETTINGS
# =============================================================================

# Set out_path folder or create it if it doesn't exist
# out_path = op.join(data_path, "out_path")
# if not op.exists(out_path):
#     os.mkdir(out_path)
        
# Remove participant without EEG from EEG analysis
if site_id == 'SA':
    if visit_id == 'V1':
        no_eeg_sbj = ['SA101', 'SA102', 'SA103', 'SA104']
    elif visit_id == 'V2':
        no_eeg_sbj = ['SA104', 'SA106']
elif site_id == 'SB':
    if visit_id == 'V1':
        no_eeg_sbj = []
    elif visit_id == 'V2':
        no_eeg_sbj = []


# =============================================================================
# BIDS SETTINGS
# =============================================================================

bids_root = r'Z:\_bids_'


# =============================================================================
# MAXWELL FILTERING SETTINGS
# =============================================================================

# Set filtering method (sss/tsss)
method='sss'
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