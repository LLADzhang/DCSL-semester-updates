fileID = fopen('Job_1','r');
formatSpec = '%f';
workloadHalf_1 = fscanf(fileID,formatSpec);

fileID = fopen('Job_5','r');
formatSpec = '%f';
workloadHalf_5 = fscanf(fileID,formatSpec);


t=0:1:size(workloadHalf_1)-0.1;

fileID = fopen('Job_10','r');
formatSpec = '%f';
workloadHalf_10 = fscanf(fileID,formatSpec);


figure;
subplot(1,3,1);

plot(t,workloadHalf_1,'-x');
xlabel('Time (discrete seconds)');
ylabel('Read Ratio');
title('1 Job');
hold
subplot(1,3,2);
plot(t,workloadHalf_5,'-x');
xlabel('Time (discrete seconds)');
ylabel('Read Ratio');
title('5 Concurrent Jobs');

subplot(1,3,3);
plot(t,workloadHalf_10,'-x');
xlabel('Time (discrete seconds)');
ylabel('Read Ratio');
title('10 Concurrent Jobs');

