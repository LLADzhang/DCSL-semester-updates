[~, ~, raw] = xlsread('H_Matrix.xlsx','H_Matrix_1_22_2018','B2:M12');
HMatrix = reshape([raw{:}],size(raw));
HMatrix(1:end,:)=HMatrix(end:-1:1,:);
clear raw;

fileID = fopen('Job_5_Scale_Out.txt.scaled.txt','r');
formatSpec = '%f';
workloadHalf = round(fscanf(fileID,formatSpec)*10,0)+1;
%workload = [11*ones(2000,1); ones(1100,1); 11*ones(500,1);];%workloadHalf+1;%[12-workloadHalf; workloadHalf];
t=0:0.1:size(workloadHalf)/10-0.1;
%t=1:0.1:360
%workload=0.5*sin(t)+0.5;
%workload=workload*10;
%workload=workload/3;
%workload=round(workload,0)+8;
workload=12-workloadHalf;%workloadHalf;
%figure; plot(t,workload,'-x');

%hold;
% value=zeros(length(t)*10,1);
% 
% noise=rand(size(t'))*8;
% for i = 0:length(t)-1
%     coin = rand;
%     if(coin > 0.5)
%         value(i*10+1:(i+1)*10) = workload(i+1) + noise(i+1);
%         
%     else
%         value(i*10+1:(i+1)*10) = workload(i+1) - noise(i+1);
%     end
%     if(value(i*10+1) > 11)
%         value(i*10+1:(i+1)*10) = 11;
%     elseif value(i*10+1) < 1
%         value(i*10+1:(i+1)*10) = 1;
%     end    
% end
t=0:1:length(workload)-1;
plot(t,workload,'-r');
ylabel('H Matrix Entry Index, 1=1.0, 11=0.0, as RR');
xlabel('Time (discrete seconds)');
%[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,Co,[],HMatrix);
%figure; plot(t,timeOps,'-x');
%[ exectotalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,[1 5 1 5 1],[250 1000 1750 2500],HMatrix);

%workload=round(value);
max = 0;
maxCO= -1;

for Co=1:1:12
    
kVal=0;
Co
[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,Co,[],HMatrix);
totalOps

if (totalOps > max)
    max = totalOps;
    maxCO=Co;
    
end
end
maxCO
max
%improvement=(exectotalOps/max-1)*100
%testConfigurations=[2 5 8];
%testReconfigTimes=[20 40 60];

%[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,[Co testConfigurations],testReconfigTimes,HMatrix);
%figure; plot(t,timeOps,'-x');

%kVal=5;


kVal=1;
x_k1 = optimizeForK( kVal,workload,HMatrix,Co )

kVal=2;
x_k2 = optimizeForK( kVal,workload,HMatrix,Co )

kVal=3;
x_k3 = optimizeForK( kVal,workload,HMatrix,Co )

kVal=4;
x_k4 = optimizeForK( kVal,workload,HMatrix,Co )

kVal=5;
x_k5 = optimizeForK( kVal,workload,HMatrix,Co )

kVal=6;
x_k6 = optimizeForK( kVal,workload,HMatrix,Co )

kVal=7;
x_k7 = optimizeForK( kVal,workload,HMatrix,Co )


figure; 
subplot(4,2,1);
% plot(t,workload,'-x');
% ylabel('Workload');
% xlabel('Time (discrete seconds)');
[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,Co,[],HMatrix);
hold all; plot(t,timeOps,'-x');hold off;
ylabel('K=0');
title(['Total Ops ' num2str(totalOps)]);

subplot(4,2,2);
kVal=1;
testConfigs=[Co x_k1(1:kVal)];
testTimes=x_k1(kVal+1:end);
[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix);
hold all; plot(t,timeOps,'-x'); plot(t(testTimes),timeOps(testTimes),'d','MarkerSize',14); hold off;
ylabel('K=1');
title(['Total Ops ' num2str(totalOps)]);

subplot(4,2,3);
kVal=2;
testConfigs=[Co x_k2(1:kVal)];
testTimes=x_k2(kVal+1:end);
[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix);
hold all; plot(t,timeOps,'-x'); plot(t(testTimes),timeOps(testTimes),'d','MarkerSize',14); hold off;
ylabel('K=2');
title(['Total Ops ' num2str(totalOps)]);

subplot(4,2,4);
kVal=3;
testConfigs=[Co x_k3(1:kVal)];
testTimes=x_k3(kVal+1:end);
[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix);
hold all; plot(t,timeOps,'-x'); plot(t(testTimes),timeOps(testTimes),'d','MarkerSize',14); hold off;
ylabel('K=3');
title(['Total Ops ' num2str(totalOps)]);

subplot(4,2,5);
kVal=4;
testConfigs=[Co x_k4(1:kVal)];
testTimes=x_k4(kVal+1:end);
[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix);
hold all; plot(t,timeOps,'-x'); plot(t(testTimes),timeOps(testTimes),'d','MarkerSize',14); hold off;
ylabel('K=4');
title(['Total Ops ' num2str(totalOps)]);

subplot(4,2,6);
kVal=5;
testConfigs=[Co x_k5(1:kVal)];
testTimes=x_k5(kVal+1:end);
[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix);
hold all; plot(t,timeOps,'-x'); plot(t(testTimes),timeOps(testTimes),'d','MarkerSize',14); hold off;
ylabel('K=5');
title(['Total Ops ' num2str(totalOps)]);

subplot(4,2,7);
kVal=6;
testConfigs=[Co x_k6(1:kVal)];
testTimes=x_k6(kVal+1:end);
[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix);
hold all; plot(t,timeOps,'-x'); plot(t(testTimes),timeOps(testTimes),'d','MarkerSize',14); hold off;
ylabel('K=5');
title(['Total Ops ' num2str(totalOps)]);

subplot(4,2,8);
kVal=7;
testConfigs=[Co x_k7(1:kVal)];
testTimes=x_k7(kVal+1:end);
[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix);
hold all; plot(t,timeOps,'-x'); plot(t(testTimes),timeOps(testTimes),'d','MarkerSize',14); hold off;
ylabel('K=5');
title(['Total Ops ' num2str(totalOps)]);



totalOpsVal=[];
for k=1:7
    kVal=k;
    xVar=eval(['x_k' num2str(k)]);
    testConfigs=[Co xVar(1:kVal)];
    testTimes=xVar(kVal+1:end);
[ totalOpsVal(k)]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix);
end

[ zeroOps ]=calculateTotalOps(workload,Co,[],HMatrix);
totalOpsVal=[zeroOps totalOpsVal];

figure; plot([1:8]-1,totalOpsVal,'--x','LineWidth',2);
xlabel('K value');
ylabel('Total Ops');