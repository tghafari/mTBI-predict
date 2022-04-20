function presentingStr = make_texture_images(cfgScreen, cfgStim, cfgExp)  
% presentingStr = make_texture_images(cfgScreen, cfgStim, cfgExp)   
% makes textures of visual stim and cue

for readImg = 1:cfgExp.numStim  % create an openGL texture for stim images
    for frm = 1:length(cfgStim.visStimR{readImg})
    presentingStr.visStimR{readImg}{frm} = Screen('MakeTexture', cfgScreen.window, cfgStim.visStimR{readImg}{frm});
    presentingStr.visStimL{readImg}{frm} = Screen('MakeTexture', cfgScreen.window, cfgStim.visStimL{readImg}{frm});
    end
end
for stim = 1:cfgExp.numStim  % create an openGL texture for cue images
    presentingStr.cueStim{stim} = Screen('MakeTexture', cfgScreen.window, cfgStim.cueStim{stim});
end

end