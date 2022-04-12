function cfgStim = read_visual_stim(cfgFile, cfgExp, cfgStim)
% cfgStim = read_visual_stim(cfgFile, cfgExp, cfgStim)
% randomly reads the visual stimuli
% inputs are the directory of stimuli images and number of trials/stim

fileDirStim = dir(cfgFile.stim);
fileDirCue = dir(cfgFile.cue);

cfgStim.visStim = cell(length(fileDirStim) - 3, 1);  % preallocation
cfgStim.visStimR = cell(length(fileDirStim) - 3, 1);  % preallocation
cfgStim.visStimL = cell(length(fileDirStim) - 3, 1);  % preallocation
cfgStim.cueStim = cell(cfgExp.numStim, 1);  % preallocation

% read right and left images separately
for spd = 3:cfgStim.stimRotSpeed:length(fileDirStim) - 2
    cfgStim.visStim{spd-2} = imread(fileDirStim(spd).name);  
%     cfgStim.visStimR{spd-2} = imread(fileDirStim(spd).name);  
%     cfgStim.visStimL{spd-2} = imread(fileDirStim(spd).name);
end
cfgStim.visStim = cfgStim.visStim(~cellfun('isempty', cfgStim.visStim'));  % remove indices that are empty due to reading images based on speed
cfgStim.visStimR = cfgStim.visStimR(~cellfun('isempty', cfgStim.visStimR'));  
cfgStim.visStimL= cfgStim.visStimL(~cellfun('isempty', cfgStim.visStimL'));

rng('shuffle')
cfgStim.cueRndIdx = randi(2, cfgExp.numStim, 1) + 2;  % random index for cue, +2 is to remove unwanted files - 3:left, 4:right

for stim = 1:cfgExp.numStim
    cfgStim.cueStim{stim,1} = imread(fileDirCue(cfgStim.cueRndIdx(stim)).name);  % read cue randomly
end

end