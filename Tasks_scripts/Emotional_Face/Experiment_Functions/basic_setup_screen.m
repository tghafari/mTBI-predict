function cfgScreen = basic_setup_screen(cfgScreen)
% cfgScreen = basic_setup_screen(cfgScreen);
%  sets up screen variables after OpenWindow

Screen('BlendFunction', cfgScreen.window, 'GL_SRC_ALPHA', 'GL_ONE_MINUS_SRC_ALPHA');  % blend funciton on
cfgScreen.ifi = Screen('GetFlipInterval', cfgScreen.window);  % query the frame duration
cfgScreen.refRate = 1 / cfgScreen.ifi; % query the frame refresh rate (Hz)
cfgScreen.FRDatapixx = Screen('NominalFrameRate', cfgScreen.window);  % Datapixx frame rate -- decide how to not mix up with PC screen FR
cfgScreen.waitFrm = 1;  % wait for this many frames when presenting stim
[cfgScreen.WinXpix, cfgScreen.WinYpix] = Screen('WindowSize', cfgScreen.window);  % size of the on screen window 
[xCentre, yCentre] = RectCenter(cfgScreen.windowRect);  % get centre coordinates 
cfgScreen.centre = [xCentre, yCentre];

topPriorityLevel = MaxPriority(cfgScreen.window);  % retreive the maximum priority for this program 
Priority(topPriorityLevel);

Screen('TextSize', cfgScreen.window, cfgScreen.fntSize);
HideCursor();

end
