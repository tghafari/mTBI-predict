function cfgOutput = cleanup(cfgFile, cfgExp, cfgScreen, cfgEyelink, cfgOutput, cfgTrigger, cfgTxt, cfgCue) %#ok<INUSD> 
% cfgOutput = cleanup(cfgFile, cfgExp, cfgScreen, cfgEyelink, cfgOutput, cfgTrigger, cfgTxt, cfgCue)
% saves all the variables and closes datapixx and eyelink
% last two variables are in just to be saved
sca
cfgOutput.endTmPnt = send_trigger(cfgTrigger, cfgExp, cfgTrigger.expEnd, cfgEyelink, 'end of experiment');

% check if the logfile is being overwritten
if exist([cfgFile.subDir, cfgFile.BIDSname, cfgFile.logFile], 'file') > 0
    warning('log file will be overwritten!');
    cont = input('Do you want to continue? (y/n) ','s');
    while true
        if cont == 'y'
            break
        elseif cont == 'n'
            error('The experiment aborted by operator.')
        end
    end
end

try
    save([cfgFile.subDir, cfgFile.BIDSname, cfgFile.logFile])
catch
    warning('Saving the log files failed.');
end

try
    if cfgExp.MEGLab
        if cfgScreen.backProjection
            Datapixx('DisablePropixxRearProjection');
        end
        Datapixx('RegWrRd');
        Datapixx('close');
    end
catch
    warning('Returing the Propixx to normal state failed.');
end
try
    if cfgEyelink.on
        el_stop(cfgFile)
    end
catch
    warning('Stopping the Eyelink failed');
end

end