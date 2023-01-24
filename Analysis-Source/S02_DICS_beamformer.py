"""
===============================================
S02. Using beamformer to localize oscillatory 
power modulations

This script uses DICS or LCMV to localize 
oscillatory power moduations based on spatial
filtering (DICS: in frequency domain). 

written by Tara Ghafari
adapted from flux pipeline
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
import os.path as op

import mne
from mne_bids import BIDSPath
from mne.cov import compute_covariance
from mne.beamformer import make_lcmv, apply_lcmv_cov, make_dics, apply_dics_csd
from mne.time_frequency import csd_multitaper


# subject info 
site = 'Birmingham'
subject = '04'  # subject code in mTBI project
session = '01'  # data collection session within each run
run = '01'  # data collection run for each participant
pilot = 'P' # is the data collected 'P'ilot or 'T'ask?
task = 'SpAtt'
meg_extension = '.fif'
meg_suffix = 'meg'
epo_suffix = 'epo'
fwd_suffix = 'fwd'
fs_sub = f'sub-{subject}'  # FreeSurfer subject name

inv_method = 'dics'  # which inverse method are you using? dspm/dics/lcmv
fr_band = 'alpha'  # over which frequency band you'd like to run the inverse model?

# Specify specific file names
bids_root = r'Z:\Projects\mTBI_predict\Collected_Data\MNE-bids-data' #'-anonymized'  # RDS folder for bids formatted data
bids_path = BIDSPath(subject=subject, session=session,
                     task=task, run=run, root=bids_root, 
                     suffix=meg_suffix, extension=meg_extension)
deriv_folder = op.join(bids_root, 'derivatives', 'flux-pipeline',
                       'sub-' + subject, 'task-' + task)  # RDS folder for results
input_fname = bids_path.basename.replace(meg_suffix, epo_suffix)
epo_fname = op.join(deriv_folder, input_fname)  # only used for suffices that are not recognizable to bids 
fwd_fname = epo_fname.replace(epo_suffix, fwd_suffix)

fs_sub_dir = r'Z:\Projects\mTBI_predict\Collected_Data\MRI_data\sub-04'  # FreeSurfer directory (after running recon all)


# Read epoched data + baseline correction + define frequency bands
epochs = mne.read_epochs(epo_fname, verbose=True, preload=False)

baseline_win = (-1.5, 0.)
active_win = (0., 1)
epochs.apply_baseline(baseline_win)

# Compute rank
rank = mne.compute_rank(epochs, tol=1e-6, tol_kind='relative')

if fr_band == 'alpha':
   fmin = 8
   fmax = 13
   bandwidth = 2.

elif fr_band == 'gamma':
    fmin = 60
    fmax = 90
    bandwidth = 4.
else:
    raise ValueError("Error: 'fr_band' value not valid")
        
epochs_band = epochs.copy().filter(fmin, fmax)
# Read forward model
if inv_method == 'dspm':
   space = 'surface'
else:
   space = 'volume'
fwd = mne.read_forward_solution(fwd_fname)

# Source modeling
if inv_method == 'lcmv':
    
    # Compute covariance matrices
    base_cov = compute_covariance(epochs_band, 
                                  tmin=baseline_win[0], tmax=baseline_win[1],
                                  method='empirical', rank=rank)
    active_cov = compute_covariance(epochs_band, 
                                    tmin=active_win[0], tmax=active_win[1],
                                    method='empirical', rank=rank)
    common_cov = base_cov + active_cov
    
    # Generate LCMV filter
    filters = make_lcmv(epochs_band.info, fwd, common_cov,
                        reg=0, depth=0, pich_ori='max-power',
                        rank=rank, weight_norm=None, reduce_rank=True)
    
elif inv_method == 'dics':
    
    # Compute cross-spectral density matrices
    noise_csd = csd_multitaper(epochs_band, fmin=fmin, fmax=fmax,
                               tmin=baseline_win[0], tmax=baseline_win[1],
                               n_jobs=4)
    common_csd = csd_multitaper(epochs_band, fmin=fmin, fmax=fmax,
                                tmin=baseline_win[0], tmax=active_win[1],
                                n_jobs=4)
    
    # Generate DICS filter
    filters = make_dics(epochs_band.info, fwd, common_csd.mean(),
                        noise_csd=noise_csd.mean(), reg=0, depth=0,
                        pick_ori='max-power', reduce_rank=True, rank=rank)
elif inv_method == 'dspm':
    
    #Compute covariance matrices
    base_cov = compute_covariance(epochs_band, 
                                  tmin=baseline_win[0], tmax=baseline_win[1],
                                  method='empirical', rank=rank)
    active_cov = compute_covariance(epochs_band, 
                                    tmin=active_win[0], tmax=active_win[1],
                                    method='empirical', rank=rank)
    common_cov = base_cov + active_cov
    
    # Make inverse operator
    filters = mne.minimum_norm.make_inverse_operator(epochs_band.info, 
                                                     fwd, common_cov,
                                                     loose=.2, depth=.8,
                                                     fixed=False, rank=rank,
                                                     use_cps=True)
else:
    raise ValueError("Error: 'inv_method' value not valid")
    
    
# Running the inverse method on conditions
conds=['cue onset right'],['cue onset left']
epochs_cond=[]
for count, condition in enumerate(conds):
    
    # Pick conditions of interest
    epochs_cond.insert(count,epochs[condition]) 
    cond_name = condition[0]
    
    print(f'\n\n\n### Running on task {condition}### \n\n')
    
    # Apply filter
    if inv_method == 'lcmv':
        
        # Compute covarianve matrices
        act_cov_cond = compute_covariance(epochs_cond[count],
                                          tmin=active_win[0], tmax=active_win[1],
                                          method='empirical', rank=rank)
        base_cov_cond = compute_covariance(epochs_cond[count],
                                          tmin=baseline_win[0], tmax=baseline_win[1],
                                          method='empirical', rank=rank)
        
        # Apply LCMV
        stc_act = apply_lcmv_cov(act_cov_cond, filters)
        stc_base = apply_lcmv_cov(base_cov_cond, filters)
        
    elif inv_method == 'dics':
        
        # Compute cross-spectral density matrices
        act_csd_cond = csd_multitaper(epochs_cond[count],
                                      fmin=fmin, fmax=fmax,
                                      tmin=active_win[0], tmax=active_win[1],
                                      bandwidth=bandwidth)
        base_csd_cond = csd_multitaper(epochs_cond[count],
                                      fmin=fmin, fmax=fmax,
                                      tmin=baseline_win[0], tmax=baseline_win[1],
                                      bandwidth=bandwidth)        
        
        # Apply DICS
        stc_act , freqs = apply_dics_csd(act_csd_cond.mean(), filters)
        stc_base , freqs = apply_dics_csd(base_csd_cond.mean(), filters)

    elif inv_method == 'dspm':
        
        # Compute covariance matrices
        act_cov_cond = compute_covariance(epochs_cond[count],
                                          tmin=active_win[0], tmax=active_win[1],
                                          method='empirical', rank=rank)
        base_cov_cond = compute_covariance(epochs_cond[count],
                                          tmin=baseline_win[0], tmax=baseline_win[1],
                                          method='empirical', rank=rank)
        
        # Apply dSPM
        stc_act = mne.minimum_norm.apply_inverse_cov(act_cov_cond,
                                                     epochs_cond[count].info,
                                                     filters,
                                                     method='dSPM',
                                                     pick_ori=None,
                                                     verbose=True)
        stc_base = mne.minimum_norm.apply_inverse_cov(base_cov_cond,
                                                      epochs_cond[count].info,
                                                      filters,
                                                      method='dSPM',
                                                      pick_ori=None,
                                                      verbose=True)
        
    else:
        raise ValueError("Error: 'inv_method' value is not valid")
        
        # Compute baseline correction
        stc_act /= stc_base
        
        # Define names and save source estimates
        cond_suffix = f"source_beam-{inv_method}_band-{fr_band}_cond-{cond_name}"
        src_fname = fwd_fname.replace(fwd_suffix, cond_suffix)
        src_fname = src_fname.replace(' ','_')

        stc_act.save(src_fname)         
            
        
    
    
    


















