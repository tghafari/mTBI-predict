function [resp,t,waitStart]=runGrating(cfg,condMat,startTime,time,sendTrigger,picTex,recPos,recPos_other,dotPos,act_bl_num,vbl,curr_bl_prac,eylnkMsg,logMsg,LPTtrig)

resp=0;t=0;button=1; picnum=1; sp_change=0; waitStart=999; i=time.i; j=time.j;
window=cfg.screen.window;fixTex=cfg.screen.fixTex; fixPos=cfg.screen.fixPos;
dotTex=cfg.screen.dotTex;

KbQueueFlush();%%removes all keyboard presses
KbQueueStart();%%start listening

start_resp_time=GetSecs();t=0;
pressed=0;resp=0;

othswtime1=condMat(i,j,12);
othswtime2=condMat(i,j,13);
dsp1 = condMat(i,j,14);
dsp2 = condMat(i,j,15);
starttrig=0;zerotrig=0;

while 1
    [pressed, firstpress] = KbQueueCheck(); %check response
    t=GetSecs-start_resp_time;        
    if firstpress(cfg.keys)>0
        resp=1;break;%match
    end
    
    if t <condMat(i,j,6)
        picnum=1+mod((picnum-1)+cfg.initspeed,300);
    elseif t >condMat(i,j,6) && t <cfg.endTime
        picnum=1+mod((picnum-1)+cfg.initspeed+cfg.dspeed,300);
        sp_change=sp_change+1;
    end
    
    if sp_change==1
        waitStart=GetSecs();
        eylnkMsg=['Trial ' int2str(j) ' Speed change'];
        if ~curr_bl_prac
            logMsg=[int2str(act_bl_num) ' ' int2str(j) ' ' num2str(GetSecs-time.t0) ' ' num2str(GetSecs-time.t_block)  ' ' num2str(GetSecs-time.t_trial)  ' Speed change ' int2str(condMat(i,j,6)*1000)];
            LPTtrig=cfg.LPT_tr.trig_speed_change;
            sendTrignLog(cfg,eylnkMsg,logMsg,LPTtrig,sendTrigger,0);
        end
    end
    
  
    Screen('DrawTextures', window, picTex{1,picnum}, [], recPos);
    Screen('DrawTextures', window, picTex{1,picnum}, [], recPos_other);
    Screen('DrawTexture', window, fixTex, [], fixPos);
    if t >condMat(i,j,6) && t <condMat(i,j,6)+cfg.dotTime
        Screen('DrawTexture', window, dotTex, [], dotPos);   
    end
    
    vbl = Screen('Flip', window, vbl + 0.5 * cfg.ifi);

    
    if starttrig==0 && ~curr_bl_prac
        sendTrignLog(cfg,eylnkMsg,logMsg,LPTtrig,sendTrigger,0);
        starttrig=1;
    end
    if zerotrig==0 && t>0.1 && ~curr_bl_prac
        sendTrigger(0);zerotrig=1;
    end
    
    if t >cfg.endTime
        if ~curr_bl_prac
            eylnkMsg=['Trial ' int2str(j) ' Trial End'];
            logMsg=[int2str(act_bl_num) ' ' int2str(j) ' ' num2str(GetSecs-time.t0) ' ' num2str(GetSecs-time.t_block)  ' ' num2str(GetSecs-time.t_trial)  ' Trial End '];
            LPTtrig=cfg.LPT_tr.trig_trl_end;
            sendTrignLog(cfg,eylnkMsg,logMsg,LPTtrig,sendTrigger,0);
        end
        break
    end
    
end

