function el_stop(cfgFile)
% el_stop(cfgFile)
% stop recording eye-movements, save, close graphics window, close data file and shut down tracker

Eyelink('StopRecording');
Eyelink('CloseFile');

fprintf('Receiving data file ''%s''\n', cfgFile.eyelink);  % download data file
el_status = Eyelink('ReceiveFile', cfgFile.eyelink, cfgFile.subDir, 1); %transfer file to experiment directory
if el_status > 0
    copy_status = copyfile(cfgFile.eyelink, cfgFile.subDir);  % copy eyelink file for renaming
    move_status = movefile(cfgFile.eyelink, [cfgFile.BIDSname, cfgFile.edfFile]);  % rename the eyelink file according to BIDS
    fprintf('ReceiveFile status %d & %d & %d\n', el_status, copy_status, move_status);
end
cleanup;

function cleanup
    % Cleanup routine
    Eyelink('Shutdown');  % shutdown Eyelink
    sca;
    ListenChar(0);  % restore keyboard output to Matlab:
end

end