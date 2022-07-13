function cfgEyelink = basic_setup_experiment
% cfgEyelink = basic_setup_experiment
% basics for Psychtoolbox

AssertOpenGL;PsychDefaultSetup(2);
inp1 = input('Do you want to skip sync test? y/n   ','s');
if inp1 == 'y'
    skypSinc = 1;
    warning('Sync test is skipped! Do not continue if it is an actual recording!');
    m = input('Do you want to continue? y/n   ','s');
    while true
        if m == 'y'
            break
        elseif m == 'n'
            error('The experiment aborted by operator.')
        end
    end
else
    skypSinc = 0;
end
Screen('Preference', 'SkipSyncTests', skypSinc);  % must be 0 during experiment

dummy = GetSecs; clear dummy;  % make a dummy call to GetSecs to load the .dll before we need it

inp3 = input('Do you want to use Eyelink? y/n   ','s');
if inp3 == 'y'
    cfgEyelink.on = 1;
else
    warning('Eyelink is off! Do not continue if it is an actual recording!');
    m = input('Do you want to continue? y/n   ','s');
    while true
        if m == 'y'
            cfgEyelink.on = 0;
            break
        elseif m == 'n'
            error('The experiment aborted by operator.')
        end
    end
end

end

