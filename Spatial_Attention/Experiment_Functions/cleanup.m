function cfgOutput = cleanup(cfgFile, cfgExp, cfgScreen, cfgEyelink, cfgOutput, cfgTrigger)
% cfgOutput = cleanup(cfgFile, cfgExp, cfgScreen, cfgEyelink, cfgOutput, cfgTrigger)
% saves all the variables and closes datapixx and eyelink
sca
cfgOutput.endTmPnt = send_trigger(cfgTrigger, cfgExp, cfgTrigger.off);

% check if the logfile is being overwritten
if exist([cfgFile.subDir, cfgFile.BIDSname, cfgFile.logFile], 'file') > 0
    cont = input('Warning! log file will be overwritten, do you want to continue? (y/n) ','s');
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