#!/usr/bin/python


import boto3
import os
import sys
import csv
import datetime
import io
import re
import itertools, sys

from datetime import datetime, timedelta


# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

#---------------------------------------------------------------------------------------------------------
# AUTHOR 		: L.B.Charith Deshapriya (charith079atgmail.com)
# USAGE 	   	: AWS EC2 CPU Analyzer
# DATE			: 31 Oct 2017 
#---------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------
#Global variables
#---------------------------------------------------------------------------------------------------------

total_ec2_cpu_thresh = 0;
cpu_v = 10; #threshold value
daysTocheck = 3;

if len(sys.argv) == 2:
	region = sys.argv[1];
else:
	print"--------------------------------------------------";
	print "Please provide a region ";
	print __file__+" [region]";
	print "eg:- >"+__file__+" us-west-1";
	print"--------------------------------------------------";

	sys.exit(1);


dry_run =False; #True or False, to check permissions
debug_run =False; #True or False, to enable debug prints

timestamp = '{:%Y-%m-%d-%H:%M:%S}'.format(datetime.utcnow());
ec2_fileout = region+"_ec2-cpu_usage"+timestamp+".csv";

#now = datetime.utcnow();
#past = now - timedelta(days=3);

now = datetime.utcnow();
start_time = now - timedelta(days=daysTocheck);
end_time = now + timedelta(minutes=5);

print "[]working on region: {0}".format(region);
print "";

ec2client = boto3.client('ec2',region_name=region);
cwatchclient = boto3.client('cloudwatch',region_name=region);


#---------------------------------------------------------------------------------------------------------
#Get EC2 instance info
#----------------------------------
def GetEc2():

	csv = open(ec2_fileout, "w");
	columnTitleRow = "Instance, Start_time, End_time, MaxCPU(%), MinCPU(%), AvgCPU(%), DataPointsSize, LowUsage EC2 count, Tags\n";
	csv.write(columnTitleRow);
	

	print "Retrieving EC2/CPU info for "+str(daysTocheck)+" days [Started]";
	vol_c = 0;

	#progress spinner for stdout 
	spinner = itertools.cycle(['-', '/', '|', '\\']);

	for ec2 in ec2client.describe_instances(DryRun=dry_run)['Reservations']:
		#row =[];
	 	#print(ec2);
		
		#initiate progress spinner for stdout 
	 	sys.stdout.write(spinner.next());
	 	sys.stdout.flush();

		if ec2['Instances']:
			instance=ec2['Instances'];
			reser_id=ec2['ReservationId'];
			for i in instance:	
		  		
		  		if debug_run: print "|"+reser_id+" : "+i['InstanceId'] + " : "+ i['InstanceType'] +" : "+ str(i['LaunchTime'])+" : "+str(i['State']),;
		  		

		  		#Getting clouldwatch details 
		  		csv_arr = GetCpu(i['InstanceId']);

			  	if 'Tags' in i.keys():
					Tag=i['Tags'];
					if debug_run: print "Tags:- ",;
					
					for j in Tag:	
			  			if debug_run: print j['Key'] + " : "+ j['Value'],;
			  			csv_arr.append(j['Key'] + " : "+ j['Value']);
			  			if debug_run: print ",",;	
				else:
			  		if debug_run: print "[This Instance doesn't have tags]";
			  		csv_arr.append("[This Instance doesn't have tags]");

		else:
		  	print "[This Reservations not attached to any instance]";

 		
		csv_arr.append("\n");
		csv.write(','.join(map(str, csv_arr)));

		if debug_run: break;

		#Closing progress spinner for stdout
		sys.stdout.write('\b');

	print "Retrieving EC2/CPU info for "+str(daysTocheck)+" days [Completed]";	
	total_ec2 ="Total "+str(total_ec2_cpu_thresh)+" EC2 instances are under utilizing CPUs (under "+ str(cpu_v)+"% avg 	usage) on " + region;
	print "---------------------------------------------------------------------------------------"
	print total_ec2;
	print "---------------------------------------------------------------------------------------"
	print "Please refer '"+ec2_fileout+"' for more details\n";
	csv.write("-----------------------------------------------------------------------------------------------\n");
	csv.write(total_ec2+"\n");
	csv.write("-----------------------------------------------------------------------------------------------\n");

	csv.close();



#---------------------------------------------------------------------------------------------------------
#Get Cloudwatch CPU info
#----------------------------------
def GetCpu(ins):

	global total_ec2_cpu_thresh;
	cpu_arr =[];
	csv_arr =[];
	insid = ins;

	if debug_run: print "instance: "+insid+" cpu from", start_time," to ",end_time, ":-",;

	cpu_avg = cwatchclient.get_metric_statistics(
    Namespace='AWS/EC2',
    MetricName='CPUUtilization',
    Dimensions=[{'Name': 'InstanceId', 'Value': insid}],
    StartTime=start_time,
    EndTime=end_time,
    Period=10800, #every 3H
    Statistics=['Maximum']);
    #ExtendedStatistics=['p100']);

	if debug_run: print cpu_avg;
	
	if debug_run: print "-----------------------"

	#ading instance and time info
	csv_arr.append(insid);
	csv_arr.append(start_time);
	csv_arr.append(end_time);

	if cpu_avg['Datapoints']:
		for datapoints in cpu_avg['Datapoints']:
			
			cpu_arr.append(datapoints['Maximum']);

			#print cpu_arr;	
			#print "-------------------------";
			#print "Size:",    len(cpu_arr);
			#sizec=len(cpu_arr);
			#print "Min:",     min(cpu_arr);
			#minc=min(cpu_arr);
			#print "Max:",     max(cpu_arr);
			#maxc=max(cpu_arr);
			#print "Sum:",     sum(cpu_arr);

		avgc = float(sum(cpu_arr))/len(cpu_arr) if len(cpu_arr) > 0 else float('nan');
		if avgc < cpu_v:
			total_ec2_cpu_thresh += 1;


		if debug_run: print "Min:", min(cpu_arr), " Max:", max(cpu_arr), " Average:",avgc, "lawCPU: ",total_ec2_cpu_thresh;

		csv_arr.append(max(cpu_arr));
		csv_arr.append(min(cpu_arr));
		csv_arr.append(avgc);
		csv_arr.append(len(cpu_arr));
		csv_arr.append(total_ec2_cpu_thresh);
		

	else:
		if debug_run: print "Instance ID: "+insid+" doesn't have datapoints It's seems stopped." ;
		csv_arr.append("Instance ID: "+insid+" doesn't have datapoints It's seems stopped.");
		

	return csv_arr;
#---------------------------------------------------------------------------------------------------------
GetEc2();
#---------------------------------------------------------------------------------------------------------



