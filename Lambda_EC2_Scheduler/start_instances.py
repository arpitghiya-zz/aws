#!/usr/bin/python

import boto3

def get_instance_name(id):
    ec2 = boto3.resource('ec2')
    ec2instance = ec2.Instance(id)
    instancename = ''
    for tags in ec2instance.tags:
        if tags["Key"] == 'Name':
            instancename = tags["Value"]
    return instancename
    
def lambda_handler(event, context):
    ec2client = boto3.client('ec2')
    tagkey = 'AutoRestart'
    tagvalue = 'True'
    response = ec2client.describe_instances(Filters=[
            {'Name': 'tag:'+tagkey, 'Values': [tagvalue]}
            ])
    instancelist = []
    print "Auto Start of EC2 instances"
    for reservation in (response["Reservations"]):
        for instance in reservation["Instances"]:
            if instance["State"]["Name"] != "stopped":
                print "Instance: {} not in stopped state. Skipping".format(get_instance_name(instance["InstanceId"]))
            else:
                instancelist.append(instance["InstanceId"])
    
    #stop running instances
    if len(instancelist) >0:
        ret = ec2client.start_instances(DryRun=False, InstanceIds=instancelist)
        for i in ret["StartingInstances"]:
            print "Starting instance: {}".format(get_instance_name(i["InstanceId"]))
    else:
        print "No Instance to start"