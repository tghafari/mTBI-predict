function cfgEyelink = initialise_eyelink(cfgFile, cfgEyelink, cfgScreen)
% cfgEyelink = initialise_eyelink(cfgFile, cfgEyelink, cfgScreen)
% initialise eye link, set parameters and start recording

Eyelink('Initialize');

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
        cfgEyelink.cameraDistance = 90;  % distance between participant and camera in cm
        cfgEyelink = el_start(cfgEyelink, cfgScreen, cfgFile);  % set parameters of eyelink and calibrate
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
