#!/bin/bash
#SBATCH --account quinna-camcan
#SBATCH --qos bbdefault
#SBATCH --time 90
#SBATCH --nodes 1  # ensure the job runs on a single node
#SBATCH --ntasks 1
#SBATCH --mem 8G
#SBATCH --array=0-119  # 20 subjects * 6 sessions = 120 array jobs

module purge
module load bluebear
module load FSL/6.0.5.1-foss-2021a-fslpython

set -e

# Define the base directory for MRI files
export base_dir="/rds/projects/s/sidhuc-mtbi-data/mTBI_MRI/MRI_BIDS"
output_dir="/rds/projects/j/jenseno-avtemporal-attention/Projects/mTBI-predict/collected-data/MRI-data/derivatives/MRI_lateralisations/substr_segmented"

# Calculate subjectID and sessionID from SLURM_ARRAY_TASK_ID
total_sessions=6
subjectID=$(( SLURM_ARRAY_TASK_ID / total_sessions + 1 ))  # Calculate subjectID (01 to 20)
sessionID=$(( SLURM_ARRAY_TASK_ID % total_sessions + 1 ))  # Calculate sessionID (01 to 06)

# Format subjectID and sessionID to include leading zeros
subjectID=$(printf "%02d" $subjectID)
sessionID=$(printf "%02d" $sessionID)

# Find all T1w files for this subject and session
for T1w_fpath in ${base_dir}/sub-20${subjectID}/ses-${sessionID}[NAB]/anat/sub-20${subjectID}_ses-${sessionID}[NAB]_T1w.nii.gz; do

    # Check if the file exists
    if [ -f "$T1w_fpath" ]; then
        # Create the output directory
        output_fpath="${output_dir}/sub-20${subjectID}/ses-${sessionID}"
        
        # Run fsl_anat command
        fsl_anat -i "$T1w_fpath" -o "$output_fpath" --clobber
        
    else
        echo "T1w file not found for sub-20${subjectID} ses-${sessionID}"
    fi
done

# Wildcard Handling of Session Letters: The session 
# directories have variable endings (N, A, B), so 
# we use [NAB] as a wildcard in both the session folder and the T1w filename.