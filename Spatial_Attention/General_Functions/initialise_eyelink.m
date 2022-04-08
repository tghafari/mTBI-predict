function cfgEyelink = initialise_eyelink(cfgFile, cfgEyelink, cfgScreen)
% cfgEyelink = initialise_eyelink(cfgFile, cfgEyelink, cfgScreen)
% initialise eye link, set parameters and start recording

cfgEyelink.eyeUsed = 'LEFT_EYE'; % eye used for monocular eyetracking

try
    if cfgEyelink.on
        if exist(cfgFile.edfFile, 'file') > 0  % check whether files already exist for this subject/session
            warning('Eyelink file will be overwritten');
            inp1 = input('Do you want to continue? y/n   ','s');
            if inp1 == 'n'
                sca
                error('session aborted by operator')
            end
        end
        cfgEyelink = el_start(cfgEyelink, cfgScreen, cfgFile);  % set parameters of eyelink and calibrate
    else
        warning('Eyetracker is set to off (see cfgEyelink.on)! Eyelink triggers will not be sent!');
        while true
            inp1 = input('Do you want to continue? y/n   ','s');
            if inp1 == 'y'
                cfgEyelink.on = 0;
                break
            elseif inp1 == 'n'
                sca
                error('The experiment aborted by operator.')
            end
        end
    end
    
catch
    warning('Eyetracker setup failed! Eyelink triggers will not be sent!');
    while true
        inp2 = input('Do you want to continue? y/n   ','s');
        if inp2 == 'y'
            cfgEyelink.on = 0;
            break
        elseif inp2 == 'n'
            sca
            error('The experiment aborted by operator.')
        end
    end
    
end
end
