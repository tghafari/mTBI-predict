function cfgEyelink = el_start(cfgEyelink, cfgScreen, cfgFile)
% cfgEyelink = el_start(cfgEyelink, cfgScreen, cfgFile)
% Open screen for calibration, calibrate and start recording

try
    window_EL = Screen('OpenWindow', cfgScreen.scrNum, [], cfgScreen.fullScrn);
    cfgEyelink.defaults = EyelinkInitDefaults(window_EL);  % details about the graphics environment and initializations
    ListenChar(2);  % disable key output to Matlab window:--> decide later
    
    if ~EyelinkInit  % initialise the connection with the Eyelink
        fprintf('Eyelink Init aborted.\n');
        cleanup
        return;
    else
        disp('Eyelink initizalized')
    end
    
    if exist([cfgFile.subDir, cfgFile.BIDSname, cfgFile.edfFile], 'file') > 0
        cont = input('Warning! Eyelink file will be overwritten, do you want to continue? (y/n) ','s');
   while true
        if cont == 'y'
            break
        elseif cont == 'n'
            error('The experiment aborted by operator.')
        end
    end        
    end
    
    status = Eyelink('Openfile', cfgFile.edfFile(:,2:end-7));  % open edf file to record data to--> check if needs .edf
    if ~status
        disp('EDF file opened on Eyelink computer')
    else
        error(['Could not open EDF file on Eyelink computer, error: ' int2str(status)])
    end
    
    cfgEyelink = el_set_parameters(cfgEyelink, cfgScreen);  % set custom parameters
    EyelinkDoTrackerSetup(cfgEyelink.defaults);   % calibrate the eye tracker
    Screen('Close', window_EL);  % close eyelink screen
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
