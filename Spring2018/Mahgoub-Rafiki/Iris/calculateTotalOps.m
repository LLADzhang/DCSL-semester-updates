function [ totalOps,totalPenalty,timeOps ] = calculateTotalOps( workload,configurations,reconfigStartTimes,HMatrix,Ns )
%configuration should be an index into H_matrix
assert(~any(configurations > size(HMatrix,2)) && ~any(configurations < 1),'Configuration out of bounds. Use integer index into H');
assert(numel(configurations) == numel(reconfigStartTimes)+1,'Must have C0 as first configuration');
assert(~any(reconfigStartTimes >= numel(workload)) && ~any(reconfigStartTimes < 1),'Must have reconfig times within domain of workload and not on the last entry');


%General config
%Ts=40; %30 second timestep
%Ns=32; %8 servers
R=2; %reconfig 2 at a time
Tr=10; %30 seconds to reconfigure a server
totalReconfigTime=Tr*Ns/R;

if(any(diff(reconfigStartTimes)<Ns/R*Tr))
    totalOps=0;
    totalPenalty=10e10;
    timeOps=zeros(numel(workload),1);

    return
else
    assert(~any(diff(reconfigStartTimes)<Ns/R*Tr),'Reconfig violates atomic constraint');
end

totalOps=0;



%Do not assume order of reconfig times
[reconfigStartTimes,configIdx]=sort(reconfigStartTimes,'ascend');
configurations(2:end)=configurations(configIdx+1);

%Map configurations to time
configAtTime=zeros(numel(workload),1);
for i=1:numel(workload)
    timeDiffs=[-inf reconfigStartTimes-i];
    timeDiffs(timeDiffs>0)=[];
    maxDiff=max(timeDiffs);
    configAtTime(i)=configurations(timeDiffs==maxDiff);
end

timeOps=zeros(numel(workload),1);
for i=1:numel(workload)
    timeOps(i)=HMatrix(workload(i),configAtTime(i));
    totalOps=totalOps+timeOps(i);
end
%totalOps_sum = totalOps
totalPenalty=0;

for i=1:numel(reconfigStartTimes)
    time=reconfigStartTimes(i);
    Ho=HMatrix(workload(time),configAtTime(max(time-1,1))); %single server
    %Hn=HMatrix(workload(time+1),configAtTime(time+1));
    %penalty=Ho; %please confirm this -> conservative but should work fine
    numSteps=ceil(Ns/R);
    if(time > 1)
        Hold = HMatrix(workload(time-1),configAtTime(time-1));          
    else
        Hold = HMatrix(workload(1),configAtTime(1));
    end
    
    Hnew = HMatrix(workload(time),configAtTime(time));
    
    penalty= abs((numSteps * ((Hnew-Hold) + (R * Hold / Ns)) )/ 2);
    
    totalOps=totalOps-penalty;
    totalPenalty=totalPenalty+penalty;
    timeOps(time:1:min(end,time+Ns/R))=timeOps(time:1:min(end,time+Ns/R))-Ho*R;
end
    
end

