function cfgScreen = visual_stim_variables
% cfgScreen = visual_stim_variables

%Primary settings
PsychDefaultSetup(2);
cfgScreen.scrNum = max(Screen('Screens'));  % get screen number - draw to the external screen if avaliable
cfgScreen.resolution = Screen('Resolution', cfgScreen.scrNum);  % get/set the on screen resolution
[cfgScreen.dispSize.width, cfgScreen.dispSize.height]...
    = Screen('DisplaySize', cfgScreen.scrNum);  % get the physical size of the screen in millimeters 
cfgScreen.distance = 60;  % set the distance from participant to the projector
cfgScreen.black = BlackIndex(cfgScreen.scrNum);
cfgScreen.white = WhiteIndex(cfgScreen.scrNum);
cfgScreen.grey = cfgScreen.white/2;
cfgScreen.fntSize = 50;
cfgScreen.destRectH = 5;  % height of destination rectangle for stimulus in visual degrees
cfgScreen.destRectW = 5;  % width of destination rectangle for stimulus in visual degrees
cfgScreen.visStimToR = [3, 2, 3, 2];  % how many visual degrees from centre is stim presented (right)
cfgScreen.visStimToL = [3, -2, 3, -2];  % how many visual degrees from centre is stim presented (left)
cfgScreen.cueToB = [0, 2, 0, 0];  % how many visual degrees from centre is cue presented (below)

end

