function cfgStim = read_visual_stim(cfgFile, cfgExp)
% cfgStim = read_visual_stim(cfgFile, cfgExp)
% randomly reads the visual stimuli
% inputs are the directory of stimuli images and number of trials/stim

fileDirStim = dir(cfgFile.stim); 
fileDirCue = dir(cfgFile.cue); 

rng('shuffle')
cfgStim.visRndIdxR = randperm(length(fileDirStim)-2, cfgExp.numStim + 2);  % make random index to read the images for right (+2 is for making up for the 2 unwanted files)
cfgStim.visRndIdxR(cfgStim.visRndIdxR < 3) = [];  % remove rndm indices for two unwanted files
cfgStim.visRndIdxL = randperm(length(fileDirStim)-2, cfgExp.numStim + 2);  % make random index to read the images for left(+2 is for making up for the 2 unwanted files)
cfgStim.visRndIdxL(cfgStim.visRndIdxL < 3) = [];  % remove rndm indices for two unwanted files
cfgStim.cueRndIdx = randi(2, cfgExp.numStim, 1) + 2;  % random index for cue, +2 is to remove unwanted files - 3:left, 4:right

cfgStim.visStimR = cell(cfgExp.numStim,1);  % preallocation
cfgStim.visStimL = cell(cfgExp.numStim,1);  % preallocation
cfgStim.cueStim = cell(cfgExp.numStim,1);  % preallocation

% randomly read visual stimuli into stimulus struct
for stim=1:cfgExp.numStim
    cfgStim.visStimR{stim,1} = imread(fileDirStim(cfgStim.visRndIdxR(stim)).name);  % read right and left images separately
    cfgStim.visStimL{stim,1} = imread(fileDirStim(cfgStim.visRndIdxL(stim)).name);
    cfgStim.cueStim{stim,1} = imread(fileDirCue(cfgStim.cueRndIdx(stim)).name);
end

end