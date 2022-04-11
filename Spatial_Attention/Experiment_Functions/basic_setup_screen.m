function cfgScreen = basic_setup_screen(cfgScreen, window)
% cfgScreen = basic_setup_screen(cfgScreen, window, );
%  sets up screen variables after OpenWindow

Screen('BlendFunction',window,'GL_SRC_ALPHA','GL_ONE_MINUS_SRC_ALPHA');  % blend funciton on
cfgScreen.ifi = Screen('GetFlipInterval',window);  % query the frame duration
cfgScreen.FRDatapixx = Screen('NominalFrameRate',window);  % Datapixx frame rate -- decide how to not mix up with PC screen FR
cfgScreen.waitFrm = 1;  % wait for this many frames when presenting stim

topPriorityLevel = MaxPriority(window);  % retreive the maximum priority for this program 
Priority(topPriorityLevel);

Screen('TextSize',window,cfgScreen.fntSize);
HideCursor();

end

% %consider adding these
% %Size of the window
% [cfg.screen.Xpix, cfg.screen.Ypix]=Screen('WindowSize',window);
% 
% %Centre of the window
% [cfg.screen.xCentre,cfg.screen.yCentre]=RectCenter(windowRect);