function [cfgCue, cfgExp, cfgTrigger] = read_cue(cfgFile, cfgExp, cfgCue, cfgTrigger)
% [cfgCue, cfgExp, cfgTrigger] = read_cue(cfgFile, cfgExp, cfgCue, cfgTrigger)
% randomly reads the cue

fileDirCue = dir([cfgFile.cue, '*.jpg']);
cfgCue.cueStim = cell(cfgExp.numStim, 1);  % preallocation

% read cue images 
rng('shuffle')
cfgCue.cueRndIdx = randperm(cfgExp.numStim);  % random index for cue - 1:right, 2:left

% Make sure there's an equal number of 1 and 2 in cfgStim.cueRndIdx
cfgCue.cueRndIdx(mod(cfgCue.cueRndIdx, 2) == 0) = 2;
cfgCue.cueRndIdx(mod(cfgCue.cueRndIdx, 2) ~= 0) = 1;

% Get catch trial indices for right and left
right_catch_ind = find(cfgCue.cueRndIdx == 1);
left_catch_ind = find(cfgCue.cueRndIdx == 2);

% Add catch trials (10% of trials) - equal number for right and left
right_catch_ind = right_catch_ind(2:10:end);
left_catch_ind = left_catch_ind(2:10:end);
cfgExp.catchTrial = zeros(cfgExp.numStim, 1);  % in cfgExp.catchTrial: 0=>target present 1=>catch trials
cfgExp.catchTrial([right_catch_ind,left_catch_ind])=1;

for stim = 1:cfgExp.numStim
    cfgCue.cueStim{stim,1} = imread(fileDirCue(cfgCue.cueRndIdx(stim)).name);  % read cue randomly
end

% collect correct responses for questions in the corresponding row +
% triggers
cfgExp.corrResp = cell(cfgExp.numStim, 3);
cfgTrigger.cuesDir = cell(cfgExp.numStim, 2);

cfgExp.corrResp(find(cfgCue.cueRndIdx == 1), 1) = {'RightArrow'};
cfgExp.corrResp(find(cfgCue.cueRndIdx == 1), 2) = {'7&'};
cfgExp.corrResp(find(cfgCue.cueRndIdx == 1), 3) = {'b'};
cfgExp.corrResp(find(cfgCue.cueRndIdx == 2), 1) = {'LeftArrow'};
cfgExp.corrResp(find(cfgCue.cueRndIdx == 2), 2) = {'4$'};
cfgExp.corrResp(find(cfgCue.cueRndIdx == 2), 3) = {'e'};
cfgExp.corrResp(find(cfgExp.catchTrial == 1), [1, 2]) = {'no resp'};
cfgTrigger.cuesDir(find(cfgCue.cueRndIdx == 1), 1) = {'101'};  % trigger codes are 101 -> cue right, 102 -> cue left
cfgTrigger.cuesDir(find(cfgCue.cueRndIdx == 2), 1) = {'102'};  % trigger codes are 101 -> cue right, 102 -> cue left
cfgTrigger.cuesDir(find(cfgCue.cueRndIdx == 1), 2) = {'Right'};  % trigger message for Eyelink
cfgTrigger.cuesDir(find(cfgCue.cueRndIdx == 2), 2) = {'Left'};  

end