# -*- coding: utf-8 -*-
"""
===============================================
05. Applying MaxFilter

this code uses MaxFilter to reduce artifacts from
environmental sources and sensor noise

adapted by Alice Waitt for Aston
written by Tara Ghafari
adapted from flux pipeline
==============================================
ToDos:
    1) generate the report and save concat files
    again
Questions:
    1) 
    2) raw.info['dev_head_t'] is not align for 
    two runs. what should be done?
    3) how come there are more gradio and
    magneto sensors after filtering?
"""
#%%
import os
import os.path as op
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import mne
from mne_bids import BIDSPath, read_raw_bids
import mne.preprocessing as preproc

# fill these out
site = 'Aston'
subject = '2001'  # subject code in mTBI project
session = '04A'  # data collection session within each run
run = '01'  # data collection run for each participant
task = 'CRT' #'rest'
meg_suffix = 'meg'
meg_extension = '.fif'
deriv_suffix = 'raw_sss'
head_pos_suffix = 'head_pos'  # name for headposition file

#Added this to manually select additional bad channels from acq/Elekta maxfilter
bad_chans_extra = ["MEG0931", "MEG1311", "MEG1331", "MEG1421", "MEG1431", "MEG2621", "MEG1441", "MEG1033", "MEG2513", "MEG2322", "MEG2033"]

sss = False #True #
rprt = True #False 

platform = 'laptop' # 'bluebear' #are you using 'bluebear', 'windows' or 'laptop'?

#%%
# Specify specific file names
if platform == 'bluebear':
    rds_dir = r'/rds/projects/s/sidhuc-mtbi-data' # \\its-rds.bham.ac.uk\rdsprojects\s\sidhuc-mtbi-data' #'/rds/projects/j/jenseno-avtemporal-attention'
    data_root = op.join(rds_dir, r'Alice_Aston_testing')
    # mTBI_root = op.join(rds_dir, r'Projects/mTBI-predict')
    # data_root = op.join(mTBI_root, 'collected-data')
elif platform == 'laptop':
    rds_dir = r'C:\Users\waitta\Documents\ClusterDocs'
    data_root = op.join(rds_dir, 'BearTestSub')
#elif platform == 'windows':
#    rds_dir = 'Z:'
#    data_root = r'C:\Users\waitta\Documents\ClusterDocs\BearTestSub' #r'/clinical/vol113/raw-sub-data/'

bids_root = op.join(data_root, 'BIDS', 'task_BIDS')  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, datatype='meg',
                     suffix=meg_suffix, extension=meg_extension)
bids_fname = bids_path.basename.replace(meg_suffix, deriv_suffix)  # only used for suffices that are not recognizable to bids 

deriv_root = op.join(bids_root, 'derivatives')  # RDS folder for results
if not op.exists(op.join(deriv_root , 'sub-' + subject, 'ses-' +session, 'task-' + task,'run-' + run)):
    os.makedirs(op.join(deriv_root , 'sub-' + subject, 'ses-' +session, 'task-' + task,'run-' + run))
deriv_folder = op.join(deriv_root , 'sub-' + subject, 'ses-' +session, 'task-' + task,'run-' + run)
deriv_fname = op.join(deriv_folder, bids_fname)
head_pos_fname = deriv_fname.replace(deriv_suffix, head_pos_suffix)

# Define the fine calibration and cross-talk compensation files 
crosstalk_file = op.join(bids_path.directory, 'sub-' + subject +'_ses-' + session + 
                         '_acq-crosstalk_meg.fif')  
calibration_file = op.join(bids_path.directory, 'sub-' + subject +'_ses-' + session + 
                           '_acq-calibration_meg.dat')  

# read and raw data 
"""only do the if run==2 for this part (as an example) for other sections
 do it manually, unless you have many 2-run subjects"""
if run == '02':
    bids_path2 = bids_path.copy().update(run='02')
    if op.exists(bids_path2):    
       raw1 = read_raw_bids(bids_path=bids_path, extra_params={'preload':True},
                               verbose=True)  #'fif files will be read with'
                                              #'allow_maxshield=True by default'                          
       raw2 = read_raw_bids(bids_path=bids_path2, extra_params={'preload':True},
                        verbose=True)
       raw2.info['dev_head_t'] = raw1.info['dev_head_t']  # to solve the error about head position not being aligned
       raw = mne.io.concatenate_raws([raw1, raw2])
else:
    # if task == 'rest':
    #    raw_root = '/clinical/vol113/raw-sub-data/BIDS/task_BIDS/derivatives-test/'
    #    raw_rest = BIDSPath(subject=subject, session=session,
    #                  task=task, run=run, root=raw_root, datatype='meg',
    #                  suffix=meg_suffix, extension=meg_extension)
    #    raw = read_raw_bids(bids_path=raw_rest, extra_params={'preload':True},
    #                        verbose=True)
    # else:    
    
    raw = read_raw_bids(bids_path=bids_path, extra_params={'preload':True},
                           verbose=True)
#%%    
if task == 'rest':
    events_suffix = 'events'
    events_extension = '.tsv'
    events_bids_path = bids_path.copy().update(suffix=events_suffix,
                                            extension=events_extension)
    events_file = pd.read_csv(events_bids_path, sep='\t')
    event_onsets = events_file[['onset', 'value', 'trial_type']]
    rest_st_time = event_onsets.loc[event_onsets['trial_type'].str.contains('rest_start'),
                                                'onset'].to_numpy()
    #t_min = np.round(rest_st_time, decimals=3)
    #t_max = np.round(rest_st_time+(60*5), decimals=3)
    t_min = rest_st_time
    t_max = rest_st_time+(60*5)
    raw.crop(tmin=float(t_min), tmax=float(t_max))
elif task=='CRT':
    events_suffix = 'events'
    events_extension = '.tsv'
    # Passing the TSV file to read_csv() with tab separator
    events_bids_path = bids_path.copy().update(suffix=events_suffix,
                                            extension=events_extension)
    events_file = pd.read_csv(events_bids_path, sep='\t')
    event_onsets = events_file[['onset', 'value', 'trial_type']]
    crt_st_time = event_onsets.loc[event_onsets['trial_type'].str.contains('block_number_1'),
                                            'onset'].to_numpy()
    crt_end_time = event_onsets.loc[event_onsets['trial_type'].str.contains('experiment_end'),
                                            'onset'].to_numpy()
    t_min = crt_st_time
    t_max = crt_end_time
    raw.crop(tmin=float(t_min), tmax=float(t_max))
   
#%%
# Identify and show faulty sensors using max filtering 
"""to identify bad channels it is best to use concatenated files (in case of
multiple meg files) and then run the maxfilter for files separately (works
better on separate files) 
"""
auto_noisy_chs, auto_flat_chs, auto_scores = preproc.find_bad_channels_maxwell(
    raw.copy(), cross_talk=crosstalk_file, calibration=calibration_file,
    return_scores=True, verbose=True)

print('noisy = ', auto_noisy_chs)
print('flat = ', auto_flat_chs)
len(auto_noisy_chs) + len(auto_flat_chs)

# set noisy and flat channels as 'bads' in the data set
#all_bads = sorted(np.unique(auto_noisy_chs + auto_flat_chs + bad_chans_extra))

raw.info['bads'] = []
raw.info['bads'].extend(auto_noisy_chs + auto_flat_chs + bad_chans_extra)
#raw.info['bads'] = all_bads
# picks = mne.pick_channels(raw.info["ch_names"], include = [bad_chans_extra]) #include=[bad_chans_extra])
# raw.copy().crop(tmin = 60, tmax=240).filter(l_freq=0.1, h_freq=150).plot(order=all_bads, n_channels=len(all_bads),title="raw")  # should be filtered bcz of cHPI high freq noise


# Edit here to manually add other bad channels identified in recording
print('bads = ', raw.info['bads'])
len(raw.info['bads'])

# we might need to change MEGIN magnetometer coil types (type 3022 and 3023 to 3024) 
# to ensure compatibility across systems
raw.fix_mag_coil_types()

#%%
if sss:  # which maxwell filtering to use? sss or tsss
    # Apply the Maxfilter with fine calibration and cross-talk reduction (SSS)
    raw_sss = preproc.maxwell_filter(raw, cross_talk=crosstalk_file,
                                     calibration=calibration_file, verbose=True)
    raw_sss.info['bads']=[]
    raw_sss.info['bads'].extend(auto_noisy_chs + auto_flat_chs + bad_chans_extra)
    #raw_sss.save(deriv_fname, overwrite=True)
    
    # Plot power spectra of raw data and after maxwell filterting for comparison
    fig, ax = plt.subplots(2,2)
    fig = raw.compute_psd(fmax=60, n_fft=1000).plot(axes=ax[:,0], show=True)
    fig = raw_sss.compute_psd(fmax=60, n_fft=1000).plot(axes=ax[:,1], show=True)
    ax[1,0].set_xlabel(' \nPSD before filtering')
    ax[1,1].set_xlabel(' \nPSD after filtering')
    fig.set_tight_layout(True)#(False)
    plt.show()
    
    # Remove cHPI frequencies and save sss/tsss file
    raw_sss_filtered = raw_sss.copy().filter(0.3,100)  
    raw_sss_filtered.save(deriv_fname, overwrite=True)
    
else:  # tsss
    # Apply Spatiotemporal SSS by passing st_duration to maxwell_filter
    raw_tsss = preproc.maxwell_filter(raw, cross_talk=crosstalk_file, st_duration=20,
                                     calibration=calibration_file, verbose=True)
    raw_tsss.info['bads']=[]
    raw_tsss.info['bads'].extend(auto_noisy_chs + auto_flat_chs + bad_chans_extra)
    #raw_tsss.save(deriv_fname, overwrite=True)

    # Plot power spectra of raw data and after maxwell filterting for comparison
    fig, ax = plt.subplots(2,2)
    fig = raw.compute_psd(fmax=60, n_fft=1000).plot(axes=ax[:,0], show=True)
    fig = raw_tsss.compute_psd(fmax=60, n_fft=1000).plot(axes=ax[:,1], show=True)
    ax[1,0].set_xlabel(' \nPSD before filtering')
    ax[1,1].set_xlabel(' \nPSD after filtering')
    fig.set_tight_layout(True)#(False)
    plt.show()
    
    # Remove cHPI frequencies and save sss/tsss file
    raw_tsss_filtered = raw_tsss.copy().filter(0.3,100)  
    raw_tsss_filtered.save(deriv_fname, overwrite=True)

#%%
# Plotting head position during each run using cHPI info
chpi_freqs, ch_idx, chpi_codes = mne.chpi.get_chpi_info(info=raw.info)
print(f"cHPI coil frequencies extracted from raw: {chpi_freqs} Hz")

# Get amplitude of cHPI
chpi_amplitudes = mne.chpi.compute_chpi_amplitudes(raw)

# Compute time-varying HPI coil locations from amplitudes
chpi_locs = mne.chpi.compute_chpi_locs(raw.info, chpi_amplitudes)

# Compute head position from the coil locations
"""
These head positions can then be used with mne.preprocessing.maxwell_filter()
to compensate for movement, or with mne.preprocessing.annotate_movement() to
mark segments as bad that deviate too much from the average head position.
"""
head_pos = mne.chpi.compute_head_pos(raw.info, chpi_locs, verbose=True)
mne.chpi.write_head_pos(head_pos_fname, head_pos)

# Calculate one output for head position
""" 
Average across all timepoints for x, y, and z
which are head_pos[:,4:7]. then calculate the combined
movement in three axes and average and std
"""
head_pos_avg_three_planes = np.mean(head_pos[:,4:7],axis=0)
head_pos_std_three_planes = np.std(head_pos[:,4:7],axis=0)
head_pos_avg_cmbnd_three_planes = np.sqrt(np.sum(head_pos_avg_three_planes**2))
head_pos_std_cmbnd_three_planes = np.sqrt(np.sum(head_pos_std_three_planes**2))

#fig, axs = plt.subplots(figsize=(10, 6))
mne.viz.plot_head_positions(head_pos, mode="traces", show=False)
# Plot average_movement as an annotation
plt.annotate(f'Average movement: {head_pos_avg_cmbnd_three_planes:.2f}', xy=(0.1, 0.2), xycoords='axes fraction')

# Plot std_dev_movement as an annotation
plt.annotate(f'Std deviation of movement: {head_pos_std_cmbnd_three_planes:.2f}', xy=(0.1, 0.05), xycoords='axes fraction')

fig_head_pos = plt.gcf()
# Show the plot
plt.show()

# fig_head_pos = mne.viz.plot_head_positions(head_pos, mode="traces")
#fig_head_pos = mne.viz.plot_head_positions(head_pos, mode="field")

#%%
if sss:
    fig_freq, ax = plt.subplots(4,5)
    fig_freq = raw.compute_psd().plot_topomap(axes=ax[0,:], show=True, ch_type="grad", 
                                            normalize=False, contours=0)
    fig_freq = raw_sss.compute_psd().plot_topomap(axes=ax[1,:], show=True, ch_type="grad", 
                                            normalize=False, contours=0)
    fig_freq = raw.compute_psd().plot_topomap(axes=ax[2,:], show=True, ch_type="mag", 
                                            normalize=False, contours=0)
    fig_freq = raw_sss.compute_psd().plot_topomap(axes=ax[3,:], show=True, ch_type="mag", 
                                            normalize=False, contours=0)

    fig.set_tight_layout(True)#(False)
    plt.show()

    fig_freq_grad, ax = plt.subplots(2,5)
    fig_freq_grad = raw.compute_psd().plot_topomap(axes=ax[0,:], show=True, ch_type="grad", 
                                            normalize=False, contours=0)
    fig_freq_grad = raw_sss.compute_psd().plot_topomap(axes=ax[1,:], show=True, ch_type="grad", 
                                            normalize=False, contours=0)

    fig_freq_mag, ax = plt.subplots(2,5)
    fig_freq_mag = raw.compute_psd().plot_topomap(axes=ax[0,:], show=True, ch_type="mag", 
                                            normalize=False, contours=0)
    fig_freq_mag = raw_sss.compute_psd().plot_topomap(axes=ax[1,:], show=True, ch_type="mag", 
                                            normalize=False, contours=0)
else:
    #tsss
    fig_freq, ax = plt.subplots(4,5)
    fig_freq = raw.compute_psd().plot_topomap(axes=ax[0,:], show=True, ch_type="grad", 
                                            normalize=False, contours=0)
    fig_freq = raw_tsss.compute_psd().plot_topomap(axes=ax[1,:], show=True, ch_type="grad", 
                                            normalize=False, contours=0)
    fig_freq = raw.compute_psd().plot_topomap(axes=ax[2,:], show=True, ch_type="mag", 
                                            normalize=False, contours=0)
    fig_freq = raw_tsss.compute_psd().plot_topomap(axes=ax[3,:], show=True, ch_type="mag", 
                                            normalize=False, contours=0)

    fig.set_tight_layout(True)#(False)
    plt.show()

    fig_freq_grad, ax = plt.subplots(2,5)
    fig_freq_grad = raw.compute_psd().plot_topomap(axes=ax[0,:], show=True, ch_type="grad", 
                                            normalize=False, contours=0)
    fig_freq_grad = raw_tsss.compute_psd().plot_topomap(axes=ax[1,:], show=True, ch_type="grad", 
                                            normalize=False, contours=0)

    fig_freq_mag, ax = plt.subplots(2,5)
    fig_freq_mag = raw.compute_psd().plot_topomap(axes=ax[0,:], show=True, ch_type="mag", 
                                            normalize=False, contours=0)
    fig_freq_mag = raw_tsss.compute_psd().plot_topomap(axes=ax[1,:], show=True, ch_type="mag", 
                                            normalize=False, contours=0)
# fig_freq.supylabel(' \nRaw grad topomap', position=(0.02,0.8))

# ax[1,0].set_xlabel(' \nRaw mag topomap')
# ax[2,0].set_xlabel(' \nSSS grad topomap')
# ax[3,0].set_xlabel(' \nSSS mag topomap')
# ax[0,0].set_xlabel(' \nRaw grad topomap')
# ax[0,0].set_xlabel(' \nRaw mag topomap')
# ax[0,0].set_xlabel(' \nSSS grad topomap')
# ax[0,0].set_xlabel(' \nSSS mag topomap')
# fig.set_tight_layout(True)#(False)
# plt.show()
# ax[1,0].set_xlabel(' \nSSS mag      Raw mag     SSS grad    Raw grad')
# fig_freq.supylabel(' \nRaw grad topomap', position=(0.02,0.8))
# fig_topo_raw_grad = raw.compute_psd().plot_topomap(ch_type="grad", normalize=False, contours=0)
# fig_topo_sss_grad = raw_sss.compute_psd().plot_topomap(ch_type="grad", normalize=False, contours=0)

# fig_topo_raw_mag = raw.compute_psd().plot_topomap(ch_type="mag", normalize=False, contours=0)
# fig_topo_sss_mag = raw_sss.compute_psd().plot_topomap(ch_type="mag", normalize=False, contours=0)

#%%
# Filter data for the report
if rprt:
   report_root = op.join(data_root, 'mne-reports') # r'/clinical/vol113/test-mne-reports'#mne-python-MEG-Reports'  # RDS folder for reports
   if not op.exists(op.join(report_root , 'sub-' + subject, 'ses-' +session, 'task-' + task, 'run-' + run)): #added ses
       os.makedirs(op.join(report_root , 'sub-' + subject, 'ses-' +session, 'task-' + task, 'run-' + run))
   report_folder = op.join(report_root , 'sub-' + subject, 'ses-' +session, 'task-' + task, 'run-' + run)
   
   report_fname = op.join(report_folder, 
                        f'mneReport_sub-{subject}_{session}_{task}_1.hdf5')    # it is in .hdf5 for later adding images
   html_report_fname = op.join(report_folder, f'report_preproc_{session}_{task}_1.html')
   report = mne.open_report(report_fname) 

   # report_fname = op.join(report_folder, f'mneReport_sub-{subject}_ses-{session}.hdf5')    # it is in .hdf5 for later adding images
   # html_report_fname = op.join(report_folder, 'report_raw.html')
   
   if sss:
       #raw_sss.filter(0,60)
       raw.filter(0.3,100) #(0,60)
       #report = mne.Report(title=f'Subject n.{subject}')
       report.add_raw(raw=raw, title='Raw <60Hz', 
                      psd=True, butterfly=False, tags=('raw'))
       report.add_raw(raw=raw_sss_filtered, title='Max filter (sss) <60Hz', 
                      psd=True, butterfly=False, tags=('MaxFilter'))
   else:
       #raw_tsss.filter(0,60)       
       raw.filter(0.3,100) #(0,60)
       #report = mne.Report(title=f'Subject n.{subject}')
       report.add_raw(raw=raw, title='Raw <60Hz', 
                      psd=True, butterfly=False, tags=('raw'))
       report.add_raw(raw=raw_tsss_filtered, title='Max filter (tsss) <60Hz', 
                      psd=True, butterfly=False, tags=('MaxFilter'))
       
   report.add_figure(fig_head_pos, title="head position over time",
                     tags=('cHPI'), image_format="PNG")
   
   report.add_figure(fig_freq,title="PSD frequency topomaps",
                      image_format="PNG")
   
   report.save(report_fname, overwrite=True)
   report.save(html_report_fname, overwrite=True, open_browser=True)  # to check how the report looks
# %%
