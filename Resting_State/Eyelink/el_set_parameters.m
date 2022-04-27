function cfgEyelink = el_set_parameters(cfgEyelink, cfgScreen)
% cfgEyelink = el_Set_Params(cfgEyelink, cfgScreen)
% Custom parameter file for Eyelink

% set global variables for Eyelink
el = cfgEyelink.defaults;
el.eye_used = cfgEyelink.eyeUsed;  % which eye is used for eyetracking
el.calibrationtargetsize = 1;
el.calibrationtargetwidth = 0.5;
el.targetbeep = 0;
el.feedbackbeep = 0;
el.displayCalResults = 1;
el.eyeimagesize = 50;  % percentage of screen

try
disp('Updating Parameters')
EyelinkUpdateDefaults(el);
cfgEyelink.defaults = el;

% make sure we're still connected.
if Eyelink('IsConnected') ~= 1 
    warning('eyelink is not connected! restart the tracker');
    cleanup
    return;
end

% make sure that we get gaze data from the Eyelink
Eyelink('Command', 'link_sample_data = LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT'); 

% this Command is crucial to map the gaze positions from the tracker to
% screen pixel positions to determine fixation
Eyelink('Command','screen_pixel_coords = %ld %ld %ld %ld', cfgScreen.fullScrn(1) - cfgScreen.fullScrn(1), cfgScreen.fullScrn(2) - cfgScreen.fullScrn(2)...
    , cfgScreen.fullScrn(3) - cfgScreen.fullScrn(1), cfgScreen.fullScrn(4) - cfgScreen.fullScrn(2));
Eyelink('message','DISPLAY_COORDS %ld %ld %ld %ld', cfgScreen.fullScrn(1) - cfgScreen.fullScrn(1), cfgScreen.fullScrn(2) - cfgScreen.fullScrn(2)...
    , cfgScreen.fullScrn(3) - cfgScreen.fullScrn(1), cfgScreen.fullScrn(4) - cfgScreen.fullScrn(2));

% use Psychophysical setting
Eyelink('Command', 'recording_parse_type = GAZE');
Eyelink('Command', 'saccade_velocity_threshold = 22');
Eyelink('Command', 'saccade_acceleration_threshold = 3800');
Eyelink('Command', 'saccade_motion_threshold = 0.0');
Eyelink('Command', 'saccade_pursuit_fixup = 60');
Eyelink('Command', 'fixation_update_interval = 0');
Eyelink('Command', 'calibration_type = HV13');
Eyelink('Command', 'generate_default_targets = YES');
Eyelink('Command', 'enable_automatic_calibration = YES');
Eyelink('Command', 'automatic_calibration_pacing = 1000');
Eyelink('Command', 'binocular_enabled = NO');%-->might need to change to binocular
Eyelink('Command', 'use_ellipse_fitter = NO');
Eyelink('Command', 'sample_rate = 1000'); %--> set to 1000?
Eyelink('Command', 'elcl_tt_power = %d', 2); % illumination, 1 = 100%, 2 = 75%, 3 = 50%

switch cfgEyelink.eyeUsed
    case 'RIGHT_EYE'
        Eyelink('Command', 'file_event_filter = RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,INPUT');
        Eyelink('Command', 'link_event_filter = RIGHT,FIXATION,FIXUPDATE,SACCADE,BLINK,MESSAGE,INPUT');
    case  'LEFT_EYE'
        Eyelink('Command', 'file_event_filter = LEFT,FIXATION,SACCADE,BLINK,MESSAGE,INPUT');
        Eyelink('Command', 'link_event_filter = LEFT,FIXATION,FIXUPDATE,SACCADE,BLINK,MESSAGE,INPUT');
end

Eyelink('Command', 'file_sample_data  = GAZE,GAZERES,HREF,PUPIL,AREA,STATUS,INPUT');

%% other settings (these might crash)

Eyelink('Command', 'heuristic_filter = 0');
Eyelink('Command', 'pupil_size_diameter = YES');

catch
    warning('error is in el_set_params')
    cleanup
    psychrethrow(psychlasterror);
end
function cleanup
% cleanup routin for Eyelink
    Eyelink('Shutdown');  % shutdown Eyelink
    el.online = 0;
end
end

