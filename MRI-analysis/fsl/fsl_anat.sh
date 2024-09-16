#!/bin/bash
#SBATCH --account quinna-camcan
#SBATCH --qos bbdefault
#SBATCH --time 90
#SBATCH --nodes 1 # ensure the job runs on a single node
#SBATCH --ntasks 5 # this will give you circa 40G RAM and will ensure faster conversion to the .sif format

module purge
module load bluebear
module load FSL/6.0.5.1-foss-2021a-fslpython

set -e

# Define the base directory for MRI files
export base_dir="/rds/projects/s/sidhuc-mtbi-data/mTBI_MRI/MRI_BIDS"
output_dir="/rds/projects/j/jenseno-avtemporal-attention/Projects/mTBI-predict/collected-data/MRI-data/derivatives/MRI_lateralisations/substr_segmented"

# Loop through subjectIDs from 01 to 20
for subjectID in $(seq -w 01 20); do

    # Loop through sessionIDs from 01 to 06
    for sessionID in $(seq -w 01 06); do
        
        # Find all T1w files for this subject and session
        for T1w_fpath in ${base_dir}/sub-20${subjectID}/ses-${sessionID}[NAB]/anat/sub-20${subjectID}_ses-${sessionID}[NAB]_T1w.nii.gz; do
            
            # Check if the file exists
            if [ -f "$T1w_fpath" ]; then
                # Create the output directory
                output_fpath="${output_dir}/sub-20${subjectID}/ses-${sessionID}"
                mkdir -p "$output_fpath"
                
                # Run fsl_anat command
                fsl_anat -i "$T1w_fpath" -o "$output_fpath" --clobber
                
            else
                echo "T1w file not found for sub-20${subjectID} ses-${sessionID}"
            fi
        done
    done
done

# Wildcard Handling of Session Letters: The session 
# directories have variable endings (N, A, B), so 
# we use [NAB] as a wildcard in both the session folder and the T1w filename.