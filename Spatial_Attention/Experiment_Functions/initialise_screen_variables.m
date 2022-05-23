function cfgScreen = initialise_screen_variables(cfgExp)
% cfgScreen = initialise_screen_variables(cfgExp)
% introduce primary settings of screen
% resolution and screen size and distance needs modification according to
% each site


PsychDefaultSetup(2);
cfgScreen.scrNum = max(Screen('Screens'));  % get screen number - draw to the external screen if avaliable

if cfgExp.MEGLab && cfgExp.site == 1  % if collecting in Aston
    cfgScreen.distance = 100;  % set the distance from participant to the projector in cm
    cfgScreen.dispSize.width = 715;  % physical width of screen in cm
    cfgScreen.dispSize.height = 405;  % physical height of screen in cm
    cfgScreen.resolution = Screen('Resolution', cfgScreen.scrNum);  % get/set the on screen resolution

elseif cfgExp.MEGLab && cfgExp.site == 2  % if collectin in Birmingham
    cfgScreen.distance = 100;  % set the distance from participant to the projector in cm
    cfgScreen.dispSize.width = 715;  % physical width of screen in mm
    cfgScreen.dispSize.height = 405;  % physical height of screen in mm
    cfgScreen.resolution = Screen('Resolution', cfgScreen.scrNum);  % get/set the on screen resolution

elseif cfgExp.MEGLab && cfgExp.site == 3  % if collectin in Nottingham
    cfgScreen.distance = 70;  % set the distance from participant to the projector in cm
    cfgScreen.dispSize.width = 815;  % physical width of screen in mm
    cfgScreen.dispSize.height = 460;  % physical height of screen in mm
    cfgScreen.resolution = Screen('Resolution', cfgScreen.scrNum);  % get/set the on screen resolution

else
    [cfgScreen.dispSize.width, cfgScreen.dispSize.height]...
        = Screen('DisplaySize', cfgScreen.scrNum);  % get the physical size of the screen in millimeters
    cfgScreen.distance = 60;  % set the distance from participant to the monitor in cm
    cfgScreen.resolution = Screen('Resolution', cfgScreen.scrNum);  % get/set the on screen resolution

end

cfgScreen.black = BlackIndex(cfgScreen.scrNum);
cfgScreen.white = WhiteIndex(cfgScreen.scrNum);
cfgScreen.grey = cfgScreen.white/2;
cfgScreen.backgroundColor = cfgScreen.black;
cfgScreen.fntSize = 50;
cfgScreen.backProjection = 0;  % is a backprojection screen used? (1 = yes, 0 = no),
cfgScreen.propixxMode = 0;  % 2 for 480 Hz, 5 for 1440 Hz, 0 for 120 Hz

if cfgExp.task || cfgExp.train
        cfgScreen.fullScrn = [0, 0, cfgScreen.resolution.width, cfgScreen.resolution.height];  % full screen for task/ train
else
        cfgScreen.fullScrn = [300, 300, 900, 900];  % use a smaller screen during testing
end

