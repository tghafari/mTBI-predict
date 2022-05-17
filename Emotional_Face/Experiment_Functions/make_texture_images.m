function presentingStr = make_texture_images(cfgScreen, cfgStim, cfgExp)  
% presentingStr = make_texture_images(cfgScreen, cfgStim, cfgExp)   
% makes textures of visual stim and cue

for readImg = cfgExp.numStim:-1:1  % create an openGL texture for stim images
    presentingStr.visStim{readImg} = Screen('MakeTexture', cfgScreen.window, cfgStim.visStim{readImg, 2});
end

end