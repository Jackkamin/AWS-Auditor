import boto3
import datetime
from datetime import date

s3_service = boto3.client('s3')  #specify what service we will be modifying. S3
response_s3 = s3_service.list_buckets()

ec2_service = boto3.client('ec2') #specify what service we will be modifying. EC2
response = ec2_service.describe_instances()

iam_service = boto3.client('iam')
iam_users = iam_service.list_users()


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
    print(bucket['Name'], "Is", is_public, "\n")  #False, PRIVATE in this case.


#Ask AWS for a list of IAM users
#Then we can ask for the age of the user and the MFA Status.

print(" IAM Checks: \n")
for users in iam_users['Users']:
    print("User Name:", users['UserName'], "\n User ID:", users['UserId'], "\nPassword last used:", users['PasswordLastUsed'])
    key_id = iam_service.list_access_keys(UserName=users['UserName'])['AccessKeyMetadata']

    for keys in key_id: # Checks AccessKeys for the creation date and key id.
        print("Key ID:", keys['AccessKeyId'],"\n", "Creation Date:", keys['CreateDate'])
        current_date = datetime.datetime.now().date() #get current date, time
        #subtracts creation date of access key from todays date, result - key age.
        key_age = current_date - keys['CreateDate'].date()
        print("This IAM User is: ", key_age, " Days old.")

        #if key age > 30 days, flag it, if not clear.
        if key_age.days > 30:
            print("FLAGGED FOR REVIEW!")
        else:
            print("CLEAR!")






