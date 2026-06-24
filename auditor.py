import boto3

s3_service = boto3.client('s3')  #specify what service we will be modifying. S3
ec2_service = boto3.client('ec2') #specify what service we will be modifying. EC2

response_s3 = s3_service.list_buckets()
response = ec2_service.describe_instances()

# checks our AWS for running/stopped services.
for reservation in response['Reservations']: #A list of batches that was launched on creation.?
    for instance in reservation['Instances']: #instance names
        print(instance['InstanceId'], instance['State']['Name']) #print specific entries of the dict


#specifically looking to find our current buckets ['Buckets']
for bucket in response_s3['Buckets']:
    bucket_acl = s3_service.get_bucket_acl(Bucket=bucket['Name'])
# Flags if bucket is public or private.
    is_public = False

    for grant in bucket_acl['Grants']:

        grant_type = grant['Grantee']['Type']
        if grant_type == 'Group':
            is_public = True
    print(bucket['Name'], "Is", is_public)  #False, PRIVATE in this case.
