clear
clc
[~, ~, raw] = xlsread('H_Matrix.xlsx','H_Matrix_1_22_2018','B2:M12');
HMatrix = reshape([raw{:}],size(raw));
HMatrix(1:end,:)=HMatrix(end:-1:1,:);
clear raw;


fileID = fopen('Job_5_Scale_Out.txt.scaled.txt','r');
formatSpec = '%f';
workloadHalf = round(fscanf(fileID,formatSpec)*10,0)+1;
wl_length = length(workloadHalf);
%workload = [11*ones(2000,1); ones(1100,1); 11*ones(500,1);];%workloadHalf+1;%[12-workloadHalf; workloadHalf];
t=0:0.1:size(workloadHalf)/10-0.1;

workload=12-workloadHalf;

t=0:1:wl_length-1;
plot(t,workload,'-r');

fileID = fopen('Scale_Best_Ops_vs_Static.txt','w');
fprintf(fileID,'%6s \t %6s \t %6s \t %12s \t %6s \t %6s \n','Size','Scale','Iris','K','Best Static','Static_conf');
%figure;
Org_workload = workload;
Ns_sizes = [4 8 32 128 256];
for Ns_i = 1:5

Ns=Ns_sizes(Ns_i);
HMatrix = Ns/4 * HMatrix;    
Scale_Values = [-8 -6 -4 -2 1 2 4 6 8]; % -ve zoomes in, +ve zoomes out
for ii = 1:9
    
scale_wl = Scale_Time( Org_workload, Scale_Values(ii));
%plot(t,scale_wl,'-b');
workload = scale_wl;
%ylabel('H Matrix Entry Index, 1=1.0, 11=0.0, as RR');
%xlabel('Time (discrete seconds)');
%[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,Co,[],HMatrix);
%figure; plot(t,timeOps,'-x');
%[ exectotalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,[1 5 1 5 1],[250 1000 1750 2500],HMatrix);

%workload=round(value);
max = 0;
maxCO= -1;

fprintf(fileID,'Server Size: %6f \t ',Ns);
for Co=1:1:12
    
kVal=0;
%Co
[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,Co,[],HMatrix,Ns);
%totalOps

if (totalOps > max)
    max = totalOps;
    maxCO=Co;
    
end
end
Static_index = maxCO
Static_Ops=max

kVal=1;
x_k1 = optimizeForK( kVal,workload,HMatrix,Co,Ns )

kVal=2;
x_k2 = optimizeForK( kVal,workload,HMatrix,Co,Ns )

kVal=3;
x_k3 = optimizeForK( kVal,workload,HMatrix,Co,Ns )

kVal=4;
x_k4 = optimizeForK( kVal,workload,HMatrix,Co,Ns )

kVal=5;
x_k5 = optimizeForK( kVal,workload,HMatrix,Co,Ns )

kVal=6;
x_k6 = optimizeForK( kVal,workload,HMatrix,Co,Ns )

kVal=7;
x_k7 = optimizeForK( kVal,workload,HMatrix,Co,Ns )


%figure; 
%subplot(4,2,1);

Iris_Max_Ops=0;
Iris_Best_K=0;
% plot(t,workload,'-x');
% ylabel('Workload');
% xlabel('Time (discrete seconds)');
[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,Co,[],HMatrix,Ns);
%hold all; plot(t,timeOps,'-x');hold off;
ylabel('K=0');
title(['Total Ops ' num2str(totalOps)]);
if(totalOps > Iris_Max_Ops)
    Iris_Max_Ops = totalOps;
    Iris_Best_K = 0;
end

%subplot(4,2,2);
if(~isempty(x_k1))
    kVal=1;
    testConfigs=[Co x_k1(1:kVal)];
    testTimes=x_k1(kVal+1:end);
    [ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix,Ns);
    %hold all; plot(t,timeOps,'-x'); plot(t(testTimes),timeOps(testTimes),'d','MarkerSize',14); hold off;
    ylabel('K=1');
    title(['Total Ops ' num2str(totalOps)]);
    if(totalOps > Iris_Max_Ops)
        Iris_Max_Ops = totalOps;
        Iris_Best_K = kVal;
    end
end

%subplot(4,2,3);3
if(~isempty(x_k2))
    kVal=2;
    testConfigs=[Co x_k2(1:kVal)];
    testTimes=x_k2(kVal+1:end);
    [ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix,Ns);
    %hold all; plot(t,timeOps,'-x'); plot(t(testTimes),timeOps(testTimes),'d','MarkerSize',14); hold off;
    ylabel('K=2');
    title(['Total Ops ' num2str(totalOps)]);
    if(totalOps > Iris_Max_Ops)
        Iris_Max_Ops = totalOps;
        Iris_Best_K = kVal;
    end
end

%subplot(4,2,4);
if(~isempty(x_k3))
    kVal=3;
    testConfigs=[Co x_k3(1:kVal)];
    testTimes=x_k3(kVal+1:end);
    [ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix,Ns);
    %hold all; plot(t,timeOps,'-x'); plot(t(testTimes),timeOps(testTimes),'d','MarkerSize',14); hold off;
    ylabel('K=3');
    title(['Total Ops ' num2str(totalOps)]);
    if(totalOps > Iris_Max_Ops)
        Iris_Max_Ops = totalOps;
        Iris_Best_K = kVal;
    end
end

%subplot(4,2,5);
if(~isempty(x_k4))
    kVal=4;
    testConfigs=[Co x_k4(1:kVal)];
    testTimes=x_k4(kVal+1:end);
    [ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix,Ns);
    %hold all; plot(t,timeOps,'-x'); plot(t(testTimes),timeOps(testTimes),'d','MarkerSize',14); hold off;
    ylabel('K=4');
    title(['Total Ops ' num2str(totalOps)]);
    if(totalOps > Iris_Max_Ops)
        Iris_Max_Ops = totalOps;
        Iris_Best_K = kVal;
    end
end

%subplot(4,2,6);
if(~isempty(x_k5))
    kVal=5;
    testConfigs=[Co x_k5(1:kVal)];
    testTimes=x_k5(kVal+1:end);
    [ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix,Ns);
    %hold all; plot(t,timeOps,'-x'); plot(t(testTimes),timeOps(testTimes),'d','MarkerSize',14); hold off;
    ylabel('K=5');
    title(['Total Ops ' num2str(totalOps)]);
    if(totalOps > Iris_Max_Ops)
        Iris_Max_Ops = totalOps;
        Iris_Best_K = kVal;
    end
end

%subplot(4,2,7);
if(~isempty(x_k6))
    kVal=6;
    testConfigs=[Co x_k6(1:kVal)];
    testTimes=x_k6(kVal+1:end);
    [ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix,Ns);
    %hold all; plot(t,timeOps,'-x'); plot(t(testTimes),timeOps(testTimes),'d','MarkerSize',14); hold off;
    ylabel('K=5');
    title(['Total Ops ' num2str(totalOps)]);
    if(totalOps > Iris_Max_Ops)
        Iris_Max_Ops = totalOps;
        Iris_Best_K = kVal;
    end
end

%subplot(4,2,8);
if(~isempty(x_k7))
    kVal=7;
    testConfigs=[Co x_k7(1:kVal)];
    testTimes=x_k7(kVal+1:end);
    [ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix,Ns);
    %hold all; plot(t,timeOps,'-x'); plot(t(testTimes),timeOps(testTimes),'d','MarkerSize',14); hold off;
    ylabel('K=5');
    title(['Total Ops ' num2str(totalOps)]);
    if(totalOps > Iris_Max_Ops)
        Iris_Max_Ops = totalOps;
        Iris_Best_K = kVal;
    end
end

% totalOpsVal=[];
% for k=1:7
%     kVal=k;
%     xVar=eval(['x_k' num2str(k)]);
%     testConfigs=[Co xVar(1:kVal)];
%     testTimes=xVar(kVal+1:end);
% [ totalOpsVal(k)]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix,Ns);
% end
% 
% 
% [ zeroOps ]=calculateTotalOps(workload,Co,[],HMatrix,Ns);
% totalOpsVal=[zeroOps totalOpsVal];
% 
% %figure; plot([1:8]-1,totalOpsVal,'--x','LineWidth',2);
%xlabel('K value');
%ylabel('Total Ops');

fprintf(fileID,'%6f \t %6.22f \t %12f \t %6.22f \t %6f \n',ii,Iris_Max_Ops, Iris_Best_K ,Static_Ops,Static_index);

end

end

fclose(fileID);