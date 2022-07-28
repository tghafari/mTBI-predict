function presentingStr = make_texture_images(cfgScreen, cfgCue, cfgExp)  
% presentingStr = make_texture_images(cfgScreen, cfgCue, cfgExp)   
% makes textures of visual stim and cue

for stim = cfgExp.numStim:-1:1  % create an openGL texture for cue images
    presentingStr.cueStim{stim} = Screen('MakeTexture', cfgScreen.window, cfgCue.cueStim{stim});
end

end