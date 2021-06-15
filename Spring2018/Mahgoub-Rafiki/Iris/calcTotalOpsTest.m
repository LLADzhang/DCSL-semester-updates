[~, ~, raw] = xlsread('H_Matrix.xlsx','H_Matrix_1_22_2018','B2:M12');
HMatrix = reshape([raw{:}],size(raw));
HMatrix(1:end,:)=HMatrix(end:-1:1,:);
clear raw;

fileID = fopen('new_simulated_scale_2_jobs_15_.txt.scaled.txt','r');
formatSpec = '%f';
workload = round(fscanf(fileID,formatSpec)*10,0);

t=0:0.1:size(workload)/10-0.1;
%workload=0.5*sin(t)+0.5;
%workload=workload*10;
%workload=round(workload,0);
workload=11-workload;
figure; plot(t,workload,'-x');
ylabel('H Matrix Entry Index, 1=0.0, 11=1.0, as RR');
xlabel('Time (discrete seconds)');

Co=1;

[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,Co,[],HMatrix);

figure; plot(t,timeOps,'-x');

testConfigurations=[2 5 8];
testReconfigTimes=[20 40 60];

[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,[Co testConfigurations],testReconfigTimes,HMatrix);
figure; plot(t,timeOps,'-x');

kVal=3;
x_k3 = optimizeForK( kVal,workload,HMatrix,Co )

kVal=1;
x_k1 = optimizeForK( kVal,workload,HMatrix,Co )

kVal=2;
x_k2 = optimizeForK( kVal,workload,HMatrix,Co )

kVal=4;
x_k4 = optimizeForK( kVal,workload,HMatrix,Co )

kVal=5;
x_k5 = optimizeForK( kVal,workload,HMatrix,Co )

figure; 
subplot(3,2,1);
% plot(t,workload,'-x');
% ylabel('Workload');
% xlabel('Time (discrete seconds)');
[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,Co,[],HMatrix);
hold all; plot(t,timeOps,'-x');hold off;
ylabel('K=0');
title(['Total Ops ' num2str(totalOps)]);

subplot(3,2,2);
kVal=1;
testConfigs=[Co x_k1(1:kVal)];
testTimes=x_k1(kVal+1:end);
[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix);
hold all; plot(t,timeOps,'-x'); plot(t(testTimes),timeOps(testTimes),'d','MarkerSize',14); hold off;
ylabel('K=1');
title(['Total Ops ' num2str(totalOps)]);

subplot(3,2,3);
kVal=2;
testConfigs=[Co x_k2(1:kVal)];
testTimes=x_k2(kVal+1:end);
[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix);
hold all; plot(t,timeOps,'-x'); plot(t(testTimes),timeOps(testTimes),'d','MarkerSize',14); hold off;
ylabel('K=2');
title(['Total Ops ' num2str(totalOps)]);

subplot(3,2,4);
kVal=3;
testConfigs=[Co x_k3(1:kVal)];
testTimes=x_k3(kVal+1:end);
[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix);
hold all; plot(t,timeOps,'-x'); plot(t(testTimes),timeOps(testTimes),'d','MarkerSize',14); hold off;
ylabel('K=3');
title(['Total Ops ' num2str(totalOps)]);

subplot(3,2,5);
kVal=4;
testConfigs=[Co x_k4(1:kVal)];
testTimes=x_k4(kVal+1:end);
[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix);
hold all; plot(t,timeOps,'-x'); plot(t(testTimes),timeOps(testTimes),'d','MarkerSize',14); hold off;
ylabel('K=4');
title(['Total Ops ' num2str(totalOps)]);

subplot(3,2,6);
kVal=5;
testConfigs=[Co x_k5(1:kVal)];
testTimes=x_k5(kVal+1:end);
[ totalOps,totalPenalty,timeOps ]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix);
hold all; plot(t,timeOps,'-x'); plot(t(testTimes),timeOps(testTimes),'d','MarkerSize',14); hold off;
ylabel('K=5');
title(['Total Ops ' num2str(totalOps)]);


totalOpsVal=[];
for k=1:5
    kVal=k;
    xVar=eval(['x_k' num2str(k)]);
    testConfigs=[Co xVar(1:kVal)];
    testTimes=xVar(kVal+1:end);
[ totalOpsVal(k)]=calculateTotalOps(workload,testConfigs,testTimes,HMatrix);
end

[ zeroOps ]=calculateTotalOps(workload,Co,[],HMatrix);
totalOpsVal=[zeroOps totalOpsVal];

figure; plot([1:6]-1,totalOpsVal,'--x','LineWidth',2);
xlabel('K value');
ylabel('Total Ops');