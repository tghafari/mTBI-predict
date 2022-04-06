function datapixxSetup(cfgExp, cfgScreen)
% datapixxSetup(cfgExp, cfgScreen)
% inputs: are we in the MEG lab?, mode of propixx. no output

propixx_mode = 0;  % 2 for 480, 5 for 1440 Hz, 0 for normal

if cfgExp.MEGLab
    try
        Datapixx('Close');  % close all datapixx related stuff
        Datapixx('Open');
        Datapixx('SetPropixxDlpSequenceProgram',propixx_mode);
        if cfgScreen.backProjection
            Datapixx('EnablePropixxRearProjection');
        end
        Datapixx('RegWrRd')
    catch
%         cleanup(cfgExp)  % run cleanup function (will be added later)
        error('Propixx setup failed. Experiment aborted.')
    end
    
end
end