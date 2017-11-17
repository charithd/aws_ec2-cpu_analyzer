# aws_ec2-cpu_analyzer
Python (Boto3) tool to identify underutilized AWS instances.
Tool will analyze CPU usages on all EC2 instances so can identify underutilized instances for cost optimization task.Can use this tool to initially filter out the CPU underutilized instances and then analyze same with other metrics like memory to make effective decisions (Can integrate memory analysis also with this tool if you have configured custom metrics agents on instances for memory utilization monitoring)

## Getting Started

These instructions will get you a copy of the Tool up and running on your local machine.

### Prerequisites

* Install Boto3
* AWS credentials should configure on  ~/.aws/credentials [You need only read permission to aws resources]

Ref: https://boto3.readthedocs.io/en/latest/guide/quickstart.html

```
pip install boto3
```

### Running the Tool

Clone the Tool and run as below

```
./ec2-cpu-analyzer.py [region]
```

### Execution and summary output

The tool will provide a summary of available underutilized instances and CSV file report with all details.
```
./aws_analyzer.py us-west-1
```
![alt text](https://github.com/charithd/aws_ec2-cpu_analyzer/blob/master/sum.png)

Below options are configurable (inside tool)to make the decision more accurate:
* Time range to analyze CPU (Default is 3 days)
* The granularity of data points (Default is 3 hours)
* CPU Threshold value to decide underutilized (Default is 10%)

### The algorithm to decide underutilized:

The tool will retrieve Maximum CPU usage values from CloudWatch according to given range and granularity and then calculate Min, Max and Avg values using those Max data points. 
Eg:- with default options the tool will retrieve every 3 hours Max values of CPU usage for last 3 Days and calculate Min, Max, and Avg. Then calculated Avg value will use with the defined threshold to decide particular instance underutilized or not.


### Reports
The tool will generate a report [Region]_ec2-cpu_usage[timestamp].csv with Instanceid,Analyzed time range, Min/Max/Avg CPU usage and Tags.

```
[Region]_ec2-cpu_usage[timestamp].csv
```

![alt text](https://github.com/charithd/aws_ec2-cpu_analyzer/blob/master/cpu-rep.png)
