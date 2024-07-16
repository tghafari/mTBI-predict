"""
===============================================
S02. Using beamformer to localize oscillatory 
power modulations

This script uses DICS or LCMV to localize 
oscillatory power moduations based on spatial
filtering (DICS: in frequency domain). 

written by Alice
adapted from flux pipeline and Tara Ghafari
==============================================
ToDos:
    1) 
    
Issues/ contributions to community:
    1) 
    
Questions:
    1)

Notes:
    Step 1: Computing source space
    Step 2: Forward model

"""
#%%
import os.path as op

import mne
from mne_bids import BIDSPath
from mne.cov import compute_covariance
from mne.beamformer import make_lcmv, apply_lcmv_cov, make_dics, apply_dics_csd
from mne.time_frequency import csd_multitaper
import numpy as np
import matplotlib.pyplot as plt

# subject info 
site = 'Aston'
subject = '2001'  # subject code in mTBI project
session = '04A'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'T' # is the data collected 'P'ilot or 'T'ask?
task = 'CRT' #'rest'
meg_extension = '.fif'
meg_suffix = 'meg'
epo_suffix = 'epo'
fwd_suffix = 'fwd'
fs_sub = 'T1_2001' #f'sub-{subject}'  # FreeSurfer subject name
rprt = True
inv_method = 'lcmv'  # which inverse method are you using? dspm/dics/lcmv
fr_band = 'alpha' #'alpha'  # over which frequency band you'd like to run the inverse model?

platform = 'laptop' #'bluebear' # are you using 'bluebear', 'windows' or 'laptop'?

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

# Specify specific file names
bids_root = op.join(data_root, 'BIDS', 'task_BIDS')  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, 
                     suffix=meg_suffix, extension=meg_extension)
deriv_folder = op.join(bids_root ,  'derivatives', 'sub-' + subject, 
                       'ses-' +session, 'task-' + task,'run-' + run) # RDS folder for results

input_fname = bids_path.basename.replace(meg_suffix, epo_suffix)
epo_fname = op.join(deriv_folder, input_fname)  # only used for suffices that are not recognizable to bids 
fwd_fname = epo_fname.replace(epo_suffix, fwd_suffix)

fs_sub_dir = op.join(bids_root, 'sub-' + subject, 'ses-' + session, 'anat')  # FreeSurfer directory (after running recon all)

#%%
# Read epoched data + baseline correction + define frequency bands
epochs = mne.read_epochs(epo_fname, verbose=True, preload=True)#False)
#epochs.pick(picks="mag") #grad or mag

#%% testing
print(epochs)
print(epochs.event_id)
print(epochs.drop_log[-4:])
epochs.plot(n_epochs=10, events=True)
print(epochs[["cue_onset_left", "cue_onset_right"]])

#%%
baseline_win = (-0.4, -0.2) #0 #(-1.5, 0.) #(-0.5,0.) # orig data epoched to -0.5 not -1.5
active_win = (0.2, 0.4 )#0.6) #(0., 1.2)
epochs.apply_baseline(baseline_win)

#%%
# Compute rank
rank = mne.compute_rank(epochs, tol=1e-6, tol_kind='relative')

#epoch freq bands

if fr_band == 'delta':
    fmin = 1
    fmax = 4
elif fr_band == 'theta':
   fmin = 4
   fmax = 8
elif fr_band == 'alpha':
   fmin = 8
   fmax = 12
elif fr_band == 'beta':
    fmin = 13
    fmax = 30
elif fr_band == 'gamma':
    fmin = 60
    fmax = 90
else:
    raise ValueError("Error: 'fr_band' value not valid")

#For each freq
epochs_band = epochs.copy().filter(fmin, fmax)

#%%
# Read forward model
if inv_method == 'dspm':
   space = 'surface'
else:
   space = 'volume'
fwd = mne.read_forward_solution(fwd_fname)

#%%
# Source modeling
# Compute covariance matrices
base_cov = compute_covariance(epochs_band, 
                              tmin=baseline_win[0], tmax=baseline_win[1],
                              method='empirical', rank=rank)
active_cov = compute_covariance(epochs_band, 
                                tmin=active_win[0], tmax=active_win[1],
                                method='empirical', rank=rank)
common_cov = base_cov + active_cov

#test plots below show grad rank is much lower vs no of channels?
base_cov.plot(epochs.info)
active_cov.plot(epochs.info)
common_cov_plot = common_cov.plot(epochs.info)

#%% noise cov - calculated ad-hoc noise cov from data cov
n_channels = common_cov.data.shape[0]
noise_avg = np.mean(np.diag(common_cov.data))
noise_cov_diag = np.array([noise_avg] * n_channels)
#take mean of diag of data cov
noise_cov = mne.Covariance(noise_cov_diag, common_cov.ch_names,
                           epochs.info['bads'], epochs.info['projs'],
                           nfree=1e10)
#%%
# Generate LCMV filter
#filters = make_lcmv(epochs_band.info, fwd, common_cov,
#                    reg=0, depth=0, pick_ori='max-power',
#                    rank=rank, weight_norm=None, reduce_rank=True)  
filters = make_lcmv(epochs_band.info, fwd, common_cov,
                    reg=0.05, noise_cov=noise_cov, pick_ori='max-power',
                    rank=rank, weight_norm='unit-noise-gain', reduce_rank=True) #rank={'mag':69}
    
#%%    
# Running the inverse method on conditions
conds=['cue_onset_right'],['cue_onset_left']
epochs_cond=[]
for count, condition in enumerate(conds):
    
    # Pick conditions of interest
    epochs_cond.insert(count,epochs[condition]) 
    cond_name = condition[0]
    
    print(f'\n\n\n### Running on task {condition}### \n\n')
    
    # Apply filter       
    # Compute covarianve matrices
    act_cov_cond = compute_covariance(epochs_cond[count],
                                        tmin=active_win[0], tmax=active_win[1],
                                        method='empirical', rank=rank)
    base_cov_cond = compute_covariance(epochs_cond[count],
                                        tmin=baseline_win[0], tmax=baseline_win[1],
                                        method='empirical', rank=rank)
    
    # Apply LCMV
    if count ==0:
        stc_act_r = apply_lcmv_cov(act_cov_cond, filters)
        stc_base_r = apply_lcmv_cov(base_cov_cond, filters)
    elif count==1:
        stc_act_l = apply_lcmv_cov(act_cov_cond, filters)
        stc_base_l = apply_lcmv_cov(base_cov_cond, filters)
    
#%%
src = epo_fname.replace(epo_suffix, 'vol-src')
brain_lcmv_r = stc_act_r.plot(
    src = src,
    subject=fs_sub,
    subjects_dir=fs_sub_dir, 
)         
brain_lcmv_l = stc_act_l.plot(
    src = src,
    subject=fs_sub,
    subjects_dir=fs_sub_dir,    
)                
        
# %%
#test plots
#lims = [5, 15, 25] #[0.3, 0.45, 0.6]
#src = epo_fname.replace(epo_suffix, 'vol-src')

#kwargs = dict(
#    src=src,
#    subject=fs_sub,
#    subjects_dir=fs_sub_dir,
#    initial_time=0.087,
#    verbose=True,
#)

#stc_act.plot(mode="stat_map", clim=dict(kind="value", pos_lims=lims), **kwargs)

#brain_lcmv = stc_act.plot(
#    hemi="rh",
#    subjects_dir=fs_sub_dir,
#    subject=fs_sub,
#    time_label="LCMV source power in the {fr_band} frequency band",
#)
# %%
# testing parcelations

# Load in participants parcels
parc = "aparc"
labels = mne.read_labels_from_annot(fs_sub, parc=parc, subjects_dir=fs_sub_dir)
#Create New parcel
new_label_parcels = [59,15,51,63] #Parcels you want included in new parcel
hemisphere = "rh"#hemisphere new parcel is in
new_label_name = hemisphere + "-parietal regions" # this changes dependant of parcels selected.
# Set up vertices and pos as lists 
vertices = []
pos = []
#Extract and combine vertices/pos for selected labels from the participants list of labels
for l in new_label_parcels:
    vertices.append(labels[l].vertices)
    pos.append(labels[l].pos)
vertices = np.concatenate(vertices)
pos = np.concatenate(pos)
 
#Sort vertices and pos
vertices_order = np.argsort(vertices)
new_vertices = np.sort(vertices[vertices_order])
new_pos = np.sort(pos[vertices_order])
 
#create label
label = mne.Label(vertices = new_vertices, pos = new_pos, hemi = hemisphere,
          name= new_label_name, subject = "sub-" + fs_sub)
label_filename = op.join(fs_sub_dir, 'test.rh.label')  # save figures in the MRI folder

label.save(label_filename)
labelright = mne.read_label(label_filename)

#%%
# extract the time course for different labels from the stc
stc_lcue = stc_act_l.in_label(label=label)
stc_rcue = stc_act_r.in_label(label, src)

# calculate center of mass and transform to mni coordinates
vtx, _, t_lh = stc_lcue.center_of_mass("sample", subjects_dir=fs_sub_dir)
mni_lh = mne.vertex_to_mni(vtx, 0, "sample", subjects_dir=fs_sub_dir)[0]
vtx, _, t_rh = stc_rcue.center_of_mass("sample", subjects_dir=fs_sub_dir)
mni_rh = mne.vertex_to_mni(vtx, 1, "sample", subjects_dir=fs_sub_dir)[0]

# plot the activation
plt.figure()
plt.axes([0.1, 0.275, 0.85, 0.625])
hl = plt.plot(stc_act_l.times, stc_lcue.data.mean(0), "b")[0]
hr = plt.plot(stc_act_r.times, stc_rcue.data.mean(0), "g")[0]
plt.xlabel("Time (s)")
plt.ylabel("Source amplitude (dSPM)")
plt.xlim(stc_act_l.times[0], stc_act_l.times[-1])

#%%
#Brain = mne.viz.get_brain_class()
#brain = Brain(fs_sub, hemi='rh', surf='pial',
#              subjects_dir=fs_sub_dir, size=(800,600))
#brain.add_annotation(label, borders=False)

#%%
if rprt:
   report_root = op.join(data_root, 'mne-reports') # r'/clinical/vol113/test-mne-reports'#mne-python-MEG-Reports'  # RDS folder for reports
   if not op.exists(op.join(report_root , 'sub-' + subject, 'ses-' +session, 'task-' + task, 'run-' + run)): #added ses
       op.makedirs(op.join(report_root , 'sub-' + subject, 'ses-' +session, 'task-' + task, 'run-' + run))
   report_folder = op.join(report_root , 'sub-' + subject, 'ses-' +session, 'task-' + task, 'run-' + run)
   
   report_fname = op.join(report_folder, 
                        f'mneReport_sub-{subject}_{session}_{task}_1.hdf5')    # it is in .hdf5 for later adding images
   html_report_fname = op.join(report_folder, f'report_preproc_{session}_{task}_1.html')
   report = mne.open_report(report_fname) 

   report.add_figure(fig=common_cov_plot, title='covariance of mags', 
                     tags =('covariance'), section='Covariance')

   report.add_figure(fig=brain_lcmv_r, title='cue right',
                    caption='localisation of response to right arrow trials in the beta band', 
                    tags=('source-estimate'),
                    section='Source localisation'
                    )
   report.add_figure(fig=brain_lcmv_l, title='cue left',
                    caption='localisation of response to left arrow trials in the beta band', 
                    tags=('source-estimate'),
                    section='Source localisation'
                    )
   
   report.save(report_fname, overwrite=True, open_browser=True)
   report.save(html_report_fname, overwrite=True, open_browser=True) 
# %%
