"""
===============================================
01. Extract events from the stimulus channels

this code is used to check and plot the timings
of triggers and creates -eve.fif file and generates
an HTML report file

written by Tara Ghafari
adapted from Oscar Ferrante 
==============================================  
ToDos:
    1) Run the code for other tasks (emoface
                                     CRT
                                     rest
                                     noise)
Issues:
    1) generate the report when mne.Report reads
    bids event file
Contributions to Community:
    1) 
Questions:
    1) 
"""

# Import relevant Python modules
import os.path as op
import os

import mne
import matplotlib.pyplot as plt

# fill these out
site = 'Birmingham'
subj_code = 'b3b0'  # subject code generated by participant/MEG pc (without the date part)
subject = '2016'  # subject code in mTBI project (can be found from the name of the fif file)
session = '05B'  # data collection session within each run (can be found from the name of the fif file)
day = '22'  # date of data collection -> removed after anonymization
month = '03'
year = '2024'

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

report = False  # do you want to generate a report?
    
# MEG bids conversion
""" using the events extracted from the MEG file, we now convert MEG file to
bids format"""

if site == 'Nottingham':
    print("please refer to BIDS_conversion_Notts.py for data collected in Nottingham")
    
tasks = ['CRT', 'EmoFace','rest', 'SpAtt', 'noise']   # task names in fif file

for task in tasks:
    
    if task == 'rest':  # only rest has two runs        
        runs = ['01', '02']
    else:
        runs = ['01']
    
    for run in runs:

        if site == 'Birmingham':
            data_path = op.join(MEG_data_folder, year + month + day + '_' + subj_code, 
                                year[-2:] + month + day)
            file_extension = '.fif'
            file_name = op.join('sub_' + subject + '_ses_' + session +
                                '_task_' + task + '_run_' + run + '_meg')
        elif site == 'Aston':
              data_path = op.join(MEG_data_folder, subj_code)  # change this according to the folder structure in Aston
              file_extension = '.fif'
              file_name = op.join('sub_' + subject + '_ses_' + session +
                                    '_task_' + task + '_run_' + run + '_meg')
                
        # specify communal file names
        raw_fname = op.join(data_path, file_name + file_extension)
        filename_events = op.join(data_path, file_name + '-eve' + file_extension)
        
        # read raw and define the stim channel
        if 'fif' in file_extension:
            raw = mne.io.read_raw_fif(raw_fname, allow_maxshield=True, 
                                      verbose=True, preload=False)
            stim_channel = 'STI101'
        
        elif 'ds' in file_extension:
            raw = mne.io.read_raw_ctf(raw_fname, system_clock='truncate', 
                                      verbose=True, preload=True)
            stim_channel = 'UPPT002'
            
        # Read the events from stim channel
        events = mne.find_events(raw, stim_channel=stim_channel, min_duration=0.001001,
                                 consecutive=False, mask=65280,
                                 mask_type='not_and')  #' mask removes triggers associated
                                                       # with response box channel 
                                                       # (not the response triggers)'
    
        # Save the events in a dedicted FIF-file: 
        mne.write_events(filename_events, events, overwrite=True)
            
        # Report the events file
        sfreq = raw.info['sfreq']
        if report == True:
            report_root = r'Z:\Projects\mTBI_predict\results-outputs\mne-reports'  # RDS folder for reports
            if not op.exists(op.join(report_root , 'sub-' + subject, 'task-' + task)):
                os.makedirs(op.join(report_root , 'sub-' + subject, 'task-' + task))
            report_folder = op.join(report_root , 'sub-' + subject, 'task-' + task)
            report_fname = op.join(report_folder, 'report_events.html')
        
            report = mne.Report(title='Events')
            report.add_events(events=events, title='events from "events"', sfreq=sfreq)
            report.save(report_fname, overwrite=True, open_browser=True)

"""if plotting is desired:
        # Plot the raw stim channel - this line only for fif so far
        if task != 'noise': 
            raw.pick(['stim']).plot()
            
            # Visualise a part of the events-array
            plt.figure()
            plt.stem(events[:,0], events[:,2])
            plt.xlim(min(events[:,0]), min(events[:,0])+100000)
            plt.title(task)
            plt.xlabel('sample')
            plt.ylabel('Trigger value (STI101)')

plt.show()  # show all plots together
"""




