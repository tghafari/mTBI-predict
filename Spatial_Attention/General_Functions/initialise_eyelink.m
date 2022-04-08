function cfgEyelink = initialise_eyelink(cfgEyelink, cfgScreen)

try
    if cfgEyelink.on
        if exist(cfgFile.edfFile, 'file') > 0  % check whether files already exist for this subject/session
           warning( 'Warning! Eyelink file will be overwritten');
            inp = input('Do you want to continue? y/n   ','s');
            if inp == 'n'
                error('session aborted by operator')
            end
        end
        
    end
catch
end




end

% Eyelink
cfg.eylnk = 0;             % eyelink on/off
cfg.el.Eyeused = 'LEFT_EYE'; % eye used
cfg.el.edffile = cfg.sub;  % EDF filename, taken from subject data and session nr
%cfg.el.fixation_window = 4; % Size of the fixation window for online fixation control (deg vis ang) - Self--> 2 deg
cfg.el.feedback = 1; % Feedback (arrows) on (1) or off (0);
cfg.el.eyelinkKey = KbName('e'); % Key used to toggle eyelink feedback on or off during experiment.

