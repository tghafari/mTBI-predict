# -*- coding: utf-8 -*-
"""
===============================================
04. calculate volume lateralized indices

This code reads the volume of all subcortical
structures from a csv file (output of 03), 
calculates lateralization index.

written by Tara Ghafari
==============================================
"""

import numpy as np
import pandas as pd
import os.path as op

platform = 'mac'

# Define where to read and write the data
if platform == 'bluebear':
    jenseno_dir = '/rds/projects/j/jenseno-avtemporal-attention'
elif platform == 'mac':
    jenseno_dir = '/Volumes/jenseno-avtemporal-attention'

# Define where to read and write the data
volume_sheet_dir = op.join(jenseno_dir,'Projects/subcortical-structures/SubStr-and-behavioral-bias/derivatives/MRI_lateralisations/lateralisation_indices')
volume_sheet_fname = op.join(volume_sheet_dir, 'all_subs_substr_volumes_1_32.csv')
output_fname = op.join(volume_sheet_dir, 'lateralisation_volumes_1_32.csv')

labels = [10, 11, 12, 13, 16, 17, 18, 26, 49, 50, 51, 52, 53, 54, 58]
structures = ['Thal', 'Caud', 'Puta', 'Pall', 'Hipp', 'Amyg', 'Accu']

# Read the CSV file into a DataFrame
volumes_df = pd.read_csv(volume_sheet_fname)

# Select the columns excluding the 5th column
hemis_vol = volumes_df.iloc[:, np.setxor1d(range(len(labels)+1), [0,5])]
sub_IDs = volumes_df.iloc[:,0]

lateralization_volume = np.zeros((len(volumes_df), 7))

for sub in range(len(volumes_df)):
    for i in range(7):
        lateralization_volume[sub, i] = (hemis_vol.iloc[sub, i + 7] - hemis_vol.iloc[sub, i]) / \
                                        (hemis_vol.iloc[sub, i + 7] + hemis_vol.iloc[sub, i])

columns = ['SubID'] + structures
df = pd.DataFrame(np.hstack((np.array(sub_IDs).reshape(-1, 1), lateralization_volume)),
                  columns=columns)
df.set_index('SubID', inplace=True)


# Save 
df.to_csv(output_fname)   

