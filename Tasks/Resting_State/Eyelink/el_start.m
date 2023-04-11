function cfgEyelink = el_start(cfgEyelink, cfgScreen, cfgFile, cfgExp)
% cfgEyelink = el_start(cfgEyelink, cfgScreen, cfgFile, cfgExp)
% Open screen for calibration, calibrate and start recording

try
    cfgEyelink.defaults = EyelinkInitDefaults(cfgScreen.window);  % details about the graphics environment and initializations
    ListenChar(1);  % disable key output to Matlab window - change to 2 on real data collection
    
    if ~EyelinkInit  % initialise the connection with the Eyelink
        fprintf('Eyelink Init aborted.\n'); 
        cleanup
        return;
    else
        disp('Eyelink initizalized')
    end
    
    if exist([cfgFile.subDir, cfgFile.eyelink], 'file') > 0
        cont = input('Warning! Eyelink file will be overwritten, do you want to continue? (y/n) ','s');
   while true
        if cont == 'y'
            break
        elseif cont == 'n'
            error('The experiment aborted by operator.')
        end
    end        
    end
    
    status = Eyelink('Openfile', cfgFile.eyelink);  % open edf file to record data to
    if ~status
        disp('EDF file opened on Eyelink computer')
    else
        error(['Could not open EDF file on Eyelink computer, error: ' int2str(status)])
    end
    
    cfgEyelink = el_set_parameters(cfgEyelink, cfgScreen, cfgExp);  % set custom parameters
    
    disp('Starting Calibration');
    EyelinkDoTrackerSetup(cfgEyelink.defaults);
    
    disp('Start Eyetrack recording')
    Eyelink('StartRecording');    
    WaitSecs(0.1);  % record a few samples before we actually start displaying
    Eyelink('Message', 'SYNCTIME');  % mark zero-plot time in data file
    ListenChar(0);
    
catch
    warning('error is in el_start')
    cleanup
    psychrethrow(psychlasterror);
end

    function cleanup
        %cleanup routin for Eyelink
        Eyelink('Shutdown');  % shutdown Eyelink
        sca;
        ListenChar(0);  % restore keyboard output to Matlab
    end
end
