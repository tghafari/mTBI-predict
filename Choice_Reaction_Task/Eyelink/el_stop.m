function el_stop(cfgFile)
% el_stop(cfgFile)
% stop recording eye-movements, save, close graphics window, close data file and shut down tracker

Eyelink('StopRecording');
Eyelink('CloseFile');

fprintf('Receiving data file ''%s''\n', cfgFile.edfFile);  % download data file
status = Eyelink('ReceiveFile', [cfgFile.BIDSname, cfgFile.edfFile], cfgFile.subDir, 1); %transfer file to experiment directory
if status > 0
    fprintf('ReceiveFile status %d\n', status);
end
cleanup;

function cleanup
    % Cleanup routine
    Eyelink('Shutdown');  % shutdown Eyelink
    sca;
    ListenChar(0);  % restore keyboard output to Matlab:
end

end