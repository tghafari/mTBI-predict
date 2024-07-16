function setup_datapixx(cfgExp, cfgScreen)
% setup_datapixx(cfgExp, cfgScreen)
% inputs: are we in the MEG lab?

if cfgExp.MEGLab && cfgExp.site == 2  % only works in Birmingham
    try
        Datapixx('Close');  % close all datapixx related stuff
        Datapixx('Open');
        Datapixx('SetPropixxDlpSequenceProgram', cfgScreen.propixxMode);
        if cfgScreen.backProjection
            Datapixx('EnablePropixxRearProjection');
        end
        Datapixx('RegWrRd')
    catch
        error('Propixx setup failed. Experiment aborted.')
    end
    
end
end