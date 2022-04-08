function presentingStr = make_texture_images(window, cfgStim)  
% presentingStr = make_texture_images(window, cfgStim)   
% makes textures of visual stim and cue

for readImg = 1:size(cfgStim.visStimR,1)  % create an openGL texture for stim and cue images
    presentingStr.visStimR{readImg} = Screen('MakeTexture', window, cfgStim.visStimR{readImg});
    presentingStr.visStimL{readImg} = Screen('MakeTexture', window, cfgStim.visStimL{readImg});
    presentingStr.cueStim{readImg} = Screen('MakeTexture', window, cfgStim.cueStim{readImg});
end

end