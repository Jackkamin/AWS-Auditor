# TODO: Eventually this program will have full access to be able to manipulate your AWS Account, for example
# TODO: Manage Services like EC2, kill instances, load up, start or stop instances at scale. FOR NOW READONLY
# TODO: Same with S3, IAM Policies etc.
#This tool is a learning experience, The idea is to focus on learning the boto3 library to create fully functional
#AWS tools. I an by no means a python Master, so please if you have suggestions for optimisation: DM me.

import boto3
import datetime


def check_ec2(ec2_service): # Checks available Instances for your AWS Account and the state they are currently in.
    findings = [] # creates list,
    response = ec2_service.describe_instances() # response assigned to this fun, will tell us available ec2 instances
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:

            if instance['State']['Name'] == 'stopped':
                findings.append({"resource": f"instance {instance['InstanceId']}",
                                 "severity": "HIGH",
                                 "issue": "Server is currently stopped, do you still need this server?"})


    return findings

def check_s3(s3_service):
    findings = []
    response_s3 = s3_service.list_buckets()
    print(f"Found {len(response_s3['Buckets'])} bucket(s)")
    for bucket in response_s3['Buckets']:
        bucket_acl = s3_service.get_bucket_acl(Bucket=bucket['Name'])
        is_public = False

        for grant in bucket_acl['Grants']:
            if grant['Grantee']['Type'] == 'Group':
                is_public = True

        if is_public:
            findings.append({
                "resource": f"Bucket {bucket['Name']}",
                "issue": "Bucket ACL is publicly accessible",
                "severity": "HIGH"
            })

        try:
            policy = s3_service.get_bucket_policy(Bucket=bucket['Name'])

            if '"Principal":"*"' in policy['Policy'] or '"Principal": "*"' in policy['Policy']:
                findings.append({
                    "resource": f"Bucket {bucket['Name']}",
                    "issue": "Bucket policy allows public access",
                    "severity": "HIGH"
                })
        except s3_service.exceptions.from_code('NoSuchBucketPolicy'):
            pass

    return findings

def check_iam(iam_service):
    findings = []
    iam_users = iam_service.list_users()
    for users in iam_users['Users']:
        key_id = iam_service.list_access_keys(UserName=users['UserName'])['AccessKeyMetadata']
        for keys in key_id:
            current_date = datetime.datetime.now().date()
            key_age = current_date - keys['CreateDate'].date()

            if key_age.days > 30:
                findings.append({"resource": f"User {users['UserName']} - Key {keys['AccessKeyId']}",
                    "issue": f"Access key is {key_age.days} days old",
                    "severity": "MEDIUM"
                })
            mfa_devices = iam_service.list_mfa_devices(UserName=users['UserName'])
            if not mfa_devices['MFADevices']:
                findings.append({ #safety check, if >30 old
                    "resource": f"User {users['UserName']}",
                    "issue": "MFA is not enabled",
                    "severity": "HIGH"
                })

    return findings


def main():
    services = {
        'ec2': check_ec2, #ec2 check
        's3': check_s3,   #s3 check
        'iam': check_iam, #iam checks
    }

    choice = input("Which services do you want to check? (ec2, s3, iam, all): ").strip().lower()
    chosen = services.keys() if choice == 'all' else [s.strip() for s in choice.split(',')]

    for service in chosen:
        if service in services:
            client = boto3.client(service)
            results = services[service](client)
            if not results:
                print(f"[{service.upper()}] No issues found.")
            for finding in results:
                print(finding["resource"], " ", finding["issue"], " ", finding["severity"])
        else:
            print(f"Unknown service: {service}")

if __name__ == "__main__":
    main()