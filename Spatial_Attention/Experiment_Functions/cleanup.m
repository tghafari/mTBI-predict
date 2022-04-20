function cleanup(cfgFile, cfgExp, cfgScreen, cfgEyelink)
% cleanup(cfgFile, cfgExp, cfgScreen, cfgEyelink)
% saves all the variables and closes datapixx and eyelink
sca
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