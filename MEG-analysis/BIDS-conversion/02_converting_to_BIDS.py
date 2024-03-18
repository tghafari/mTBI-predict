
"""
===============================================
02. Convert raw MEG data into BIDS format

this code converts raw MEG data (.fif & .ds)
as well as T1 MRIs to BIDS format.
It also anonizes MEG and defaces MRI file.

written by Tara Ghafari
==============================================

ToDos:
    1) add MRI to bids folder
    2) check the anonimization of MEG 
    3) deface MRI with mne_bids

Issued/Contributions to community:
    1) anonymization with bids only work on the
    foler, this means we can't run the analysis
    on anonymized data because the sub number
    changes every time bids anonymizes the folder
Notes:
    CTF data is still under development by mne_bids
    team
    first run find_events and coregistration before 
    running this script
"""

import os.path as op

import matplotlib.pyplot as plt

#from nilearn.plotting import plot_anat

import mne
from mne_bids import (BIDSPath, write_raw_bids, read_raw_bids, 
                      write_meg_calibration, write_meg_crosstalk, 
                      get_anat_landmarks, write_anat)

# fill these out
site = 'Birmingham'
subj_code = 'b355'  # subject code generated by participant/MEG pc (without the date part)
subject = '2015'  # subject code in mTBI project (can be found from the name of the fif file)
session = '06B'  # data collection session within each run (can be found from the name of the fif file)
day = '13'  # date of data collection -> removed after anonymization
month = '02'
year = '2024'


MRI_convert = False  # do you also want to convert MRI for this participant?

platform = 'mac'  # are you using 'bluebear', 'mac', or 'windows'?

if platform == 'bluebear':
    rds_dir = '/rds/projects/j/jenseno-avtemporal-attention'
elif platform == 'windows':
    rds_dir = 'Z:'
elif platform == 'mac':
    rds_dir = '/Volumes/jenseno-avtemporal-attention'

# Specify specific file names
mTBI_root = op.join(rds_dir, 'Projects/mTBI-predict')
data_root = op.join(mTBI_root, 'collected-data')
MEG_data_folder = op.join(data_root, 'MEG-data/Raw-real_participants')  # RDS/storage folder for MEG data

# MEG bids conversion
""" using the events extracted from the MEG file, we now convert MEG file to
bids format"""

if site == 'Nottingham':
    print("please refer to BIDS_conversion_Notts.py for data collected in Nottingham")
    
tasks = ['CRT', 'rest', 'EmoFace', 'SpAtt', 'noise']   # task names in fif file 
BIDS_tasks = ['CRT', 'EmoFace', 'rest', 'SpAtt', 'noise']  # task names after BIDS conversion - this is used if tasks
                                                           # are named differently in the fif file.
for t, task in enumerate(tasks):
    
    if task == 'rest':
        runs = ['01', '02']
    else:
        runs = ['01']
    
    for r, run in enumerate(runs):

        if site == 'Birmingham':
            data_path = op.join(MEG_data_folder, year + month + day + '_' + subj_code, 
                                year[-2:] + month + day)
            file_extension = '.fif'
            file_name = op.join('sub_' + subject + '_ses_' + session +
                                '_task_' + task + '_run_' + run + '_meg')
        elif  site == 'Aston':
            data_path = op.join(MEG_data_folder, subj_code)  # change this according to the folder structure in Aston
            file_extension = '.fif'
            file_name = op.join('sub_' + subject + '_ses_' + session +
                                  '_task_' + task + '_run_' + run + '_meg')
    
        # specify communal file names
        raw_fname = op.join(data_path, file_name + file_extension)
        events_data = op.join(data_path, file_name + '-eve' + file_extension)
        bids_root = op.join(data_root, 'BIDS', 'task_BIDS')
        noise_bids_root = op.join(data_root, 'BIDS', 'noise_BIDS')

        # Define the fine calibration and cross-talk compensation files 
        maxfilter_folder = op.join(mTBI_root, 'programming/github/mTBI-predict/MEG-analysis/BIDS-conversion/MaxFilter')
        crosstalk_file = op.join(maxfilter_folder, 'CT_sparse_SA.fif')  #'reduces interference' 
                                                                        #'between Elekta's co-located' 
                                                                        #'magnetometer and'
                                                                        #'paired gradiometer sensor units'
        calibration_file = op.join(maxfilter_folder, 'sss_cal_SA.dat')  #'encodes site-specific'
                                                                        #'information about sensor' 
                                                                        #'orientations and calibration'
        
            
        # define bids path for tasks and empty room: for noise do not anonymize since it 
        # removes the date
        if 'noise' in task:
            raw = mne.io.read_raw_fif(raw_fname, allow_maxshield=True, 
                                      verbose=True, preload=False)
            stim_channel = 'STI101'
            noise_bids_path = BIDSPath(subject=subject, session=session,
                                       task='noise', root=noise_bids_root)
        else:
            raw = mne.io.read_raw_fif(raw_fname, allow_maxshield=True, 
                                      verbose=True, preload=False).anonymize()
            stim_channel = 'STI101'
            bids_path = BIDSPath(subject=subject, session=session,
                                 task=BIDS_tasks[t], run=run, root=bids_root)
        
        # Define events according to the event values       
        if task == 'SpAtt':
            block_num = {}
            for num in range(1,3+1):
                block_num[f'block_number_{num:01d}'] = num + 10
            
            # commented ones are only on during debugging
            other_events = {'trial_onset': 1, 
                            'cue_onset_right':101, 'cue_onset_left':102, 'cue_offset':103,
                             'catch_onset':104, 'stim_onset':201, #'stim_offset':202,
                             'dot_onset_right':211, 'dot_onset_left':212, #'dot_offset':213,
                             'response_press_onset':255, 'block_end':15,
                             'experiment_end':20, #'experiment_abort':21
                             }
            
            events_id = block_num | other_events
            
        elif task == 'CRT':
            block_num = {}
            for num in range(1,4+1):
                block_num[f'block_number_{num:01d}'] = num + 10
                
            other_events = {'trial_onset': 1, #'trial_end':2,
                            'cue_onset_right':101, 'cue_onset_left':102, #'cue_offset':103,
                            #'catch_onset':104, 
                            'response_onset_right':254, 'response_onset_left':255, 
                            'block_end':15,'experiment_end':20, #'experiment_abort':21
                            }
            
            events_id = block_num | other_events
            
        elif task == 'EmoFace':
            face_id = {}
            stim_cat = ['face_happy_id', 'face_angry_id', 'face_neutral_id']
            for count,stim in enumerate(stim_cat):
                for fid in range(35+1):  # range is an end half closed loop
                    face_id[stim+f'_{1+fid:02d}'] = fid + 110 + count*40  # starting points are 110, 150, and 190
                    
            block_num = {}
            for num in range(1,3+1):
                block_num[f'block_number_{num:01d}'] = num + 10
            
            other_events = {'trial_onset': 1, #'trial_end':2,
                            'face_onset_happy':101, 'face_onset_angry':102, 'face_onset_neutral':103, 
                            'face_male':231, 'face_female':232, 'face_offset':104, 
                            'question_onset':105,
                            'response_male_onset':254, 'response_female_onset':255, 
                            #'experiment_abort':21,
                            'block_end':15,'experiment_end':20}
            
            events_id = other_events | face_id | block_num
            
        elif task == 'rest':
                
            other_events = {'rest_start': 1, 'rest_end':2,
                            'experiment_abort':21}
            
            events_id = other_events
            
        # Write anonymized data into BIDS format
        if task == 'noise':
            write_raw_bids(raw, noise_bids_path, overwrite=True)
        else:
            write_raw_bids(raw, bids_path, events_data=events_data, 
                           event_id=events_id, overwrite=True)
        
        # Write in Maxfilter files
        write_meg_calibration(calibration_file, bids_path=bids_path, verbose=False)
        write_meg_crosstalk(crosstalk_file, bids_path=bids_path, verbose=False)
    
    

if MRI_convert:
    # MRI bids conversion
    """ using the trans file created by coregistration, we now convert T1W MRI file 
    to bids format"""
    
    trans_folder = op.join(bids_root, 'derivatives', 'flux-pipeline',
                           'sub-' + subject, 'T1w-MRI')  # RDS folder for trans file
    trans_fname = op.join(trans_folder, 'sub-' + subject + '_ses-' + session
                          + '_' + 'coreg-trans.fif')
    fs_sub_dir = r'Z:\Projects\mTBI_predict\Collected_Data\MRI_data\sub-04'  # FreeSurfer directory
    fs_sub = f'sub-{subject}'
    t1_fname = op.join(fs_sub_dir, fs_sub + '.nii')
    
    # Create the BIDSpath object
    """ creat MRI specific bidspath object and then use trans file to transform 
    landmarks from the raw file to the voxel space of the image"""
    
    t1w_bids_path = BIDSPath(subject=subject, session=session, 
                             root=bids_root, suffix='T1w')
    
    info = read_raw_bids(bids_path=bids_path, verbose=False).info
    trans = mne.read_trans(trans_fname)  
    landmarks = get_anat_landmarks(
        image=t1_fname,  # path to the nifti file
        info=info,  # MEG data file info from the subject
        trans=trans,
        fs_subject=fs_sub,
        fs_subjects_dir=fs_sub_dir)
    
    t1w_bids_path = write_anat(
        image=t1_fname, bids_path=t1w_bids_path,
        landmarks=landmarks, deface=True,
        overwrite=True, verbose=True)
    
    # Take a quick look at the MRI
    t1_nii_fname = op.join(t1w_bids_path.directory, t1w_bids_path.basename)
    
    fig, ax = plt.subplots()
    plot_anat(t1_nii_fname, axes=ax, title='Defaced')
    plt.show()