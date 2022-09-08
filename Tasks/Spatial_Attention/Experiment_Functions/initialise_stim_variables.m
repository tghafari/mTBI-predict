function cfgStim = initialise_stim_variables
% cfgStim = initialise_stim_variables
% initialise variables of cue and grating

cfgStim.stimRotSpeed = 2; % number of 360-degree rotations per second
cfgStim.destRectH = 7;  % height of destination rectangle for stimulus in visual degrees
cfgStim.destRectW = 7;  % width of destination rectangle for stimulus in visual degrees
cfgStim.destRectCueSize = 3;  % size of destination rectangle for cue
cfgStim.visStimToR = [5, 1, 5, 1];  % how many visual degrees from centre is stim presented (right)
cfgStim.visStimToL = [5, -1, 5, -1];  % how many visual degrees from centre is stim presented (left)
cfgStim.cueToB = [0, 2, 0, 2];  % how many visual degrees from centre is cue presented (below)

end

