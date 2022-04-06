function waitMoveOnEsc(cfg,timeout,time,sendTrigger)

if ~isfield(time,'i'),i=0;else i=time.i-cfg.pract;end
if ~isfield(time,'j'),j=0;else j=time.j;end
if ~isfield(time,'t_block'),t_block=0;else t_block=time.t_block;end
if ~isfield(time,'t_trial'),t_trial=0;else t_trial=time.t_trial;end
if ~isfield(time,'t0'),t0=0;else t0=time.t0;end

waitstart=GetSecs;moveon=false; window=cfg.screen.window;

while ~moveon
    [ keyIsDown, keyTime, keyCode ] = KbCheck;
    
    if keyIsDown && keyCode(cfg.escapeKey)
        cleanup(cfg);
        error('Experiment aborted by user')
    elseif keyIsDown && keyCode(cfg.pauseKey)
        eylnkMsg=['Block' int2str(i) ' Trial ' int2str(j) ' Experiment Paused'];
        logMsg=[int2str(i) ' ' int2str(j) ' ' num2str(GetSecs-t0) ' ' num2str(GetSecs-t_block)  ' ' num2str(GetSecs-t_trial) ' Experiment Paused'];
        LPTtrig=cfg.LPT_tr.trig_pause;
        sendTrignLog(cfg,eylnkMsg,logMsg,LPTtrig,sendTrigger,0.1);
        
        Screen('TextSize',window, round(cfg.screen.Xpix/60));
        DrawFormattedText(window,'Experiment paused','center','center',[1 1 1]);
        
        vbl=Screen('Flip',window);
        
        
        RestrictKeysForKbCheck(13);
        KbWait;RestrictKeysForKbCheck([]);
        %KbPressWait();
        
        Screen('DrawTexture', window, cfg.screen.fixTex, [], cfg.screen.fixPos);
        vbl = Screen('Flip', window);
        
        eylnkMsg=['Block' int2str(i) 'Trial ' int2str(j) ' Experiment Resumed'];
        logMsg=[int2str(i) ' ' int2str(j) ' ' num2str(GetSecs-t0) ' ' num2str(GetSecs-t_block)  ' ' num2str(GetSecs-t_trial) ' Experiment Resumed'];
        LPTtrig=cfg.LPT_tr.trig_resume;
        sendTrignLog(cfg,eylnkMsg,logMsg,LPTtrig,sendTrigger,0.1);
        
        WaitSecs(5);
        break
    end
    if (GetSecs-waitstart)>timeout
        moveon=true;
    end
end
end
