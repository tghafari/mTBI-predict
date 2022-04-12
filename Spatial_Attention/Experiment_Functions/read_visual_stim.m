function cfgStim = read_visual_stim(cfgFile, cfgExp, cfgScreen)
% cfgStim = read_visual_stim(cfgFile, cfgExp)
% randomly reads the visual stimuli
% inputs are the directory of stimuli images and number of trials/stim

fileDirStim = dir(cfgFile.stim); 
fileDirCue = dir(cfgFile.cue); 

rng('shuffle')
cfgStim.cueRndIdx = randi(2, cfgExp.numStim, 1) + 2;  % random index for cue, +2 is to remove unwanted files - 3:left, 4:right

cfgStim.visStimR = cell(cfgExp.numStim,1);  % preallocation
cfgStim.visStimL = cell(cfgExp.numStim,1);  % preallocation
cfgStim.cueStim = cell(cfgExp.numStim,1);  % preallocation

for stim = 4:cfgExp.numStim
    for spd = 1:cfgScreen.stimRotSpeed:length(fileDirStim) - 3
    cfgStim.visStimR{stim-3,1}{spd} = imread(fileDirStim(stim).name);  % read right and left images separately
    cfgStim.visStimL{stim-3,1}{spd} = imread(fileDirStim(stim).name);
    cfgStim.cueStim{stim-3,1} = imread(fileDirCue(cfgStim.cueRndIdx(stim-3)).name);  % read cue randomly
    end
end

end