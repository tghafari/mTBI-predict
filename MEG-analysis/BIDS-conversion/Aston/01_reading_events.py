"""
===============================================
01. Extract events from the stimulus channels

this code is used to check and plot the timings
of triggers and creates -eve.fif file and generates
an HTML report file

adapted by Alice Waitt for Aston
originally written by Tara Ghafari
adapted from Oscar Ferrante 
==============================================  

"""

# Import relevant Python modules
import os.path as op
import os
import mne
import matplotlib.pyplot as plt

# fill these out
subject = '2008'  # subject code in mTBI project
session = '06A'  # data collection session within each run
day = '10'  # date of data collection -> removed after anonymization
month = '11'
year = '2023'

data_root = r'/clinical/vol113/raw-sub-data'
MEG_data_folder = op.join(data_root, 'sub_' + subject, 'ses_' + session, 'MEG')  # RDS folder for MEG data

report = True  # do you want to generate a report?
    
# MEG bids conversion
""" using the events extracted from the MEG file, we now convert MEG file to
bids format"""

#if run == '01':
#    tasks = ['SpAtt', 'CRT', 'EmoFace','rest']   # short name of task
#elif run == '02':
#    tasks = ['rest'] #['SpAtt','rest'] for 2002_02A for wrong button presses in run 1 spatt
    
tasks = ['rest', 'CRT', 'SpAtt', 'EmoFace']   # task names in fif file

for task in tasks:
    
    if task == 'rest':  # only rest has two runs        
        runs = ['01', '02']
    #elif task == 'SpAtt':
        #runs = ['01', '02']
    else:
        runs = ['01']
    
    for run in runs:
    
        data_path = op.join(MEG_data_folder, year + month + day + '_' + subject, 
                                year[-2:] + month + day)
        file_extension = '.fif'
        file_name = op.join('sub_' + subject + '_ses_' + session +
                                '_task_' + task + '_run_' + run + '_meg')
        
        # Report folder names
        if report:
            report_root = r'/clinical/vol113/mne-python-MEG-Reports'  # RDS folder for reports
            if task =='rest':
            #if run == '02':
                if not op.exists(op.join(report_root , 'sub-' + subject, 'ses-' + session, 'task-' + task, 'run-' + run)):
                    os.makedirs(op.join(report_root , 'sub-' + subject, 'ses-' + session, 'task-' + task, 'run-' + run))
                report_folder = op.join(report_root , 'sub-' + subject, 'ses-' + session, 'task-' + task, 'run-' + run)
            else:
                if not op.exists(op.join(report_root , 'sub-' + subject, 'ses-' + session, 'task-' + task)):
                    os.makedirs(op.join(report_root , 'sub-' + subject, 'ses-' + session, 'task-' + task))    
                report_folder = op.join(report_root , 'sub-' + subject, 'ses-' + session, 'task-' + task)
               
            report_fname = op.join(report_folder, 'report_events.html')
        
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
        #check for sub 2008 06A and 2009 01A                                               
        #events_faces = mne.pick_events(events, exclude= [1,11,12, 13, 15, 20, 40, 41, 167, 168, 190, 191])
        
        # Save the events in a dedicted FIF-file: 
        mne.write_events(filename_events, events, overwrite=True)
            
        # Report the events file
        sfreq = raw.info['sfreq']
        #didn't work when report == True:
        if report:
            report = mne.Report(title='Events')
            report.add_events(events=events, title='events from "events"', sfreq=sfreq)
            report.save(report_fname, overwrite=True, open_browser=True)
        
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
            
        
        #raw.pick_types(meg=False, stim=True).plot()
        
plt.show()  # show all plots together
