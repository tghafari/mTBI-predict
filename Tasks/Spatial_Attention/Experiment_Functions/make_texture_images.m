function presentingStr = make_texture_images(cfgScreen, cfgStim, cfgExp)  
% presentingStr = make_texture_images(cfgScreen, cfgStim, cfgExp)   
% makes textures of visual stim and cue

% randomly read in R & L visual stim- this snippet should be here because of the number of frames
cfgStim.visStimMat = repmat(cfgStim.visStim, ceil(max(cfgExp.stimFrm)/100), 1);  % matrix of inward moving gratings
% create enough visual stimuli for each trial
for stm = 1:length(cfgExp.stimFrm)
    cfgStim.visStimR{stm} = cfgStim.visStimMat(1 : max(cfgExp.stimFrm) + 50);  % every cfgExp.stimSpeedFrm = one complete rotation
    cfgStim.visStimL{stm} = cfgStim.visStimMat(1 : max(cfgExp.stimFrm) + 50);  % 10 is added just to make sure there is enough stims
end

for readImg = cfgExp.numStim:-1:1  % create an openGL texture for stim images
    for frm = length(cfgStim.visStimR{readImg}):-1:1
    presentingStr.visStimR{readImg}{frm} = Screen('MakeTexture', cfgScreen.window, cfgStim.visStimR{readImg}{frm});
    presentingStr.visStimL{readImg}{frm} = Screen('MakeTexture', cfgScreen.window, cfgStim.visStimL{readImg}{frm});
    end
end
for stim = cfgExp.numStim:-1:1  % create an openGL texture for cue images
    presentingStr.cueStim{stim} = Screen('MakeTexture', cfgScreen.window, cfgStim.cueStim{stim});
end

end