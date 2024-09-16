#!/bin/bash
#SBATCH --account quinna-camcan
#SBATCH --qos bbdefault
#SBATCH --time 90
#SBATCH --nodes 1 # ensure the job runs on a single node
#SBATCH --ntasks 5 # this will give you circa 40G RAM and will ensure faster conversion to the .sif format
#SBATCH --array=0-119  # 20 subjects * 6 sessions = 120 array jobs

module purge
module load bluebear
module load FSL/6.0.5.1-foss-2021a-fslpython

set -e

# Define the location of the file
output_dir="/rds/projects/j/jenseno-avtemporal-attention/Projects/mTBI-predict/collected-data/MRI-data/derivatives/MRI_lateralisations/substr_segmented"

# Define variables for FSL command
labels=(10 11 12 13 16 17 18 26 49 50 51 52 53 54 58)
structures=("L-Thal" "L-Caud" "L-Puta" "L-Pall" "BrStem /4th Ventricle" \
    "L-Hipp" "L-Amyg" "L-Accu" "R-Thal" "R-Caud" "R-Puta" \
    "R-Pall" "R-Hipp" "R-Amyg" "R-Accu")

# Calculate subjectID and sessionID from SLURM_ARRAY_TASK_ID
total_sessions=6
subjectID=$(( SLURM_ARRAY_TASK_ID / total_sessions + 1 ))  # Calculate subjectID (01 to 20)
sessionID=$(( SLURM_ARRAY_TASK_ID % total_sessions + 1 ))  # Calculate sessionID (01 to 06)

# Format subjectID and sessionID to include leading zeros
subjectID=$(printf "%02d" $subjectID)
sessionID=$(printf "%02d" $sessionID)

first_fpath="${output_dir}/sub-20${subjectID}/ses-${sessionID}.anat/first_results"
# Find all T1w files for this subject and session

# Check if the file exists
if [ -d "$first_fpath" ]; then
    # Create the output directory
    SubVol_fpath="${output_dir}/sub-20${subjectID}/ses-${sessionID}.SubVol"
    mkdir -p "$SubVol_fpath"
    
    echo "${first_fpath} was found"

    for low in ${labels[@]}; do
        low_minus_point_five=$(echo "$low - 0.5" | bc)
        low_plus_point_five=$(echo "$low + 0.5" | bc)

        VoxVol=$(fslstats "${first_fpath}/T1_first_all_fast_firstseg.nii.gz" -l "$low_minus_point_five" -u "$low_plus_point_five" -V)
        echo "Volumetring: sub-20${subjectID}_ses-${sessionID} structure: ${low}"

    output_fname="${SubVol_fpath}/volume${low}"
    echo "$VoxVol" > "$output_fname"            
    done
    
    echo "Volumetring ${subjectID}_ses-${sessionID} done"
else
    echo "no "$first_fpath" found, continuing to the next sub"
fi
