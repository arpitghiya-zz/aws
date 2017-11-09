import boto3
import datetime
rds_client = boto3.client('rds')

def process_tags(arn):
    env = ""
    auto_restart = ""
    result = False
    tags = rds_client.list_tags_for_resource(
        ResourceName=arn
    )
    for tag in (tags["TagList"]):
        if (tag["Key"] == "Environment"):
            env = tag["Value"]
        if (tag["Key"] == "AutoRestart"):
            auto_restart = tag["Value"]
    if (env == "Test"):
        if (auto_restart == "True"):
            print "Found a Test Environment and AutoRestart Set to True - %s" %(arn)
            result = True
        else:
            print "Not Processing this Environment %s" %(arn)
            print "Environment: %s, AutoRestart: %s" %(env,auto_restart)
    else:
        print "Not Processing this Environment %s" %(arn)
        print "Environment: %s, AutoRestart: %s" %(env,auto_restart)
    return result
    
def lambda_handler(event, context):
    now = datetime.datetime.now()
    today_date = now.strftime("%Y-%m-%d")
    instances = rds_client.describe_db_instances()
    print "Stop RDS Instances on Schedule"
    for instance in (instances["DBInstances"]):
        restart = False
        arn = instance["DBInstanceArn"]
        name = instance["DBInstanceIdentifier"]
        status = instance["DBInstanceStatus"]
        print "-------------------------------------------------"
        print "Found Instance: %s" %(name)
        restart = process_tags(arn)
        if (restart == True):
            if (status != "available"):
                print "Instance %s is not in available state. Not taking any action..." %(name)
            else:
                print "Stopping %s" %(name)
                snapshot = "%s-%s" %(name,today_date)
                stop_response = rds_client.stop_db_instance(DBInstanceIdentifier=name,DBSnapshotIdentifier=snapshot)