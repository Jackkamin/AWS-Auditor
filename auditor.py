import boto3
import datetime

def check_ec2(ec2_service):
    response = ec2_service.describe_instances()
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            print(instance['InstanceId'], instance['State']['Name'])

def check_s3(s3_service):
    response_s3 = s3_service.list_buckets()
    for bucket in response_s3['Buckets']:
        bucket_acl = s3_service.get_bucket_acl(Bucket=bucket['Name'])
        is_public = False
        for grant in bucket_acl['Grants']:
            if grant['Grantee']['Type'] == 'Group':
                is_public = True
        print(bucket['Name'], "Is", is_public, "\n")

def check_iam(iam_service):
    iam_users = iam_service.list_users()
    print(" IAM Checks: \n")
    for users in iam_users['Users']:
        print("User Name:", users['UserName'], "\n User ID:", users['UserId'],
              "\nPassword last used:", users['PasswordLastUsed'])
        key_id = iam_service.list_access_keys(UserName=users['UserName'])['AccessKeyMetadata']

        for keys in key_id:
            print("Key ID:", keys['AccessKeyId'], "\n", "Creation Date:", keys['CreateDate'])
            current_date = datetime.datetime.now().date()
            key_age = current_date - keys['CreateDate'].date()
            print("This IAM User is: ", key_age, " Days old.")

            if key_age.days > 30:
                print("FLAGGED FOR REVIEW!")
            else:
                print("CLEAR!")

            mfa_devices = iam_service.list_mfa_devices(UserName=users['UserName'])
            if not mfa_devices['MFADevices']:
                print("List is empty, REVIEW")
            else:
                for mfa_device in mfa_devices['MFADevices']:
                    print("MFA CLEARED!")


def main():
    services = {
        'ec2': check_ec2,
        's3': check_s3,
        'iam': check_iam,
    }

    choice = input("Which services do you want to check? (ec2, s3, iam, all): ").strip().lower()
    chosen = services.keys() if choice == 'all' else [s.strip() for s in choice.split(',')]

    for service in chosen:
        if service in services:
            client = boto3.client(service)
            services[service](client)
        else:
            print(f"Unknown service: {service}")

if __name__ == "__main__":
    main()