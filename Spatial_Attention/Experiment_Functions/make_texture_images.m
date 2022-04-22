function presentingStr = make_texture_images(cfgScreen, cfgStim, cfgExp)  
% presentingStr = make_texture_images(cfgScreen, cfgStim, cfgExp)   
% makes textures of visual stim and cue

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