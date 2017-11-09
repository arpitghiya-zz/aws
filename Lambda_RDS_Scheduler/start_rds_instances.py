import boto3
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
    instances = rds_client.describe_db_instances()
    print "Start RDS Instances on Schedule"
    for instance in (instances["DBInstances"]):
        restart = False
        arn = instance["DBInstanceArn"]
        name = instance["DBInstanceIdentifier"]
        status = instance["DBInstanceStatus"]
        print "-------------------------------------------------"
        print "Found Instance: %s" %(name)
        restart = process_tags(arn)
        if (restart == True):
            if (status != "stopped"):
                print "Instance %s is not in stopped state. Not taking any action..." %(name)
            else:
                print "Starting %s" %(name)
                start_response = rds_client.start_db_instance(DBInstanceIdentifier=name)