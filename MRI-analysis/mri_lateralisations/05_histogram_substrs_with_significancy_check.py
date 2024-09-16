# -*- coding: utf-8 -*-
"""
===============================================
05. histogram substrs

This code read the lateralized volumes from a 
csv file, plots a histogram for each substr and
checks for significant differences with normal 
distribution

written by Tara Ghafari
==============================================
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os.path as op
from scipy import stats
from scipy.stats import shapiro

platform = 'mac'

# Define where to read and write the data
if platform == 'bluebear':
    jenseno_dir = '/rds/projects/j/jenseno-avtemporal-attention'
elif platform == 'mac':
    jenseno_dir = '/Volumes/jenseno-avtemporal-attention'

# Define where to read and write the data
volume_sheet_dir = op.join(jenseno_dir,'Projects/subcortical-structures/SubStr-and-behavioral-bias/derivatives/MRI_lateralisations/lateralisation_indices')
lat_sheet_fname = op.join(volume_sheet_dir, 'lateralisation_volumes_1_32.csv')
df = pd.read_csv(lat_sheet_fname)
lateralisation_volume = df.iloc[:,1:8].to_numpy()

colormap = ['#FFD700', '#8A2BE2', '#191970', '#8B0000', '#6B8E23', '#4B0082', '#ADD8E6']
structures = ['Thal', 'Caud', 'Puta', 'Pall', 'Hipp', 'Amyg', 'Accu']
p_values = []
p_values_shapiro =[]

# null hypothesis (H0) mean value
throw_out_outliers = False
null_hypothesis_mean = 0.0
t_stats = []
t_p_vals = []

# wilcoxon p-vals
null_hypothesis_median = 0.0
wilcox_p_vals = []

fig, axs = plt.subplots(2, 4)
fig.set_figheight(6)
fig.set_figwidth(10)

for his in range(7):       
    # Define plot settings
    ax = axs[his // 4, his % 4]
    ax.set_title(structures[his], fontsize=12)#, fontname='Calibri')
    ax.set_xlabel('Lateralisation Volume', fontsize=12)#, fontname='Calibri')
    ax.set_ylabel('# Subjects', fontsize=12)#, fontname='Calibri')
    ax.axvline(x=0, color='k', linewidth=0.25, linestyle=':')
    
    # Remove nans and plot normalized (z-scored) distributions
    valid_lateralisation_volume = lateralisation_volume[~np.isnan(lateralisation_volume[:, his]), his]
    lateralisation_volume_hist = np.histogram(valid_lateralisation_volume, bins=6, density=False)
    
    # Throw out the outliers
    mean_lateralisation_volume = np.nanmean(valid_lateralisation_volume)
    std_lateralisation_volume = np.nanstd(valid_lateralisation_volume)
    threshold = mean_lateralisation_volume - (2.5 * std_lateralisation_volume)
    valid_lateralisation_volume[:][valid_lateralisation_volume[:] <= threshold] = np.nan
    
    # Perform the ranksum test
    k2, p = stats.normaltest(valid_lateralisation_volume, nan_policy='omit')
    p_values.append(p)
    stat, shapiro_p = shapiro(valid_lateralisation_volume)
    p_values_shapiro.append(shapiro_p)
    
    # 1 sample t-test for left/right lateralisation
    t_statistic, t_p_value = stats.ttest_1samp(valid_lateralisation_volume, null_hypothesis_mean)
    t_stats.append(t_statistic)
    t_p_vals.append(t_p_value)
    
    # one sample wilcoxon signed rank (for non normal distributions)
    _, wilcox_p = stats.wilcoxon(valid_lateralisation_volume - null_hypothesis_median,
                                 zero_method='wilcox', correction=False)
    wilcox_p_vals.append(wilcox_p)
  
    # plot histogram
    x = lateralisation_volume_hist[1]
    y = lateralisation_volume_hist[0]
    ax.bar(x[:-1], y, width=np.diff(x), color=colormap[his])
    
#    # plot a normal density function
#    mu, std = stats.norm.fit(valid_lateralisation_volume)
#   pdf = stats.norm.pdf(x, mu, std)
#   ax.plot(x, pdf, 'r-', label='Normal Fit', linewidth=0.5)        
    
    txt = r'$p = {:.2f}$'.format(p)
    ax.text(min(ax.get_xlim()) + max(ax.get_xlim()), max(ax.get_ylim()), txt,
            fontsize=8)#, fontname='Calibri')
    txt = r'$1samp_p = {:.2f}$'.format(t_p_value)
    #ax.text(min(ax.get_xlim()) + 0.2 * max(ax.get_xlim()), max(ax.get_ylim()) - 50, txt,
    #        fontsize=10)#, fontname='Calibri'), fontname='Calibri')
    txt = r'$wilcox_p = {:.2f}$'.format(wilcox_p)
    #ax.text(min(ax.get_xlim()) + 0.2 * max(ax.get_xlim()), max(ax.get_ylim()) - 60, txt,
    #        fontsize=10)#, fontname='Calibri'), fontname='Calibri')
    
    ax.tick_params(axis='both', which='both', length=0)
    ax.set_axisbelow(True)

plt.tight_layout()
plt.show()
