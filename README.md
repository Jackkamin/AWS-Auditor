# AWS Account Auditor

A Python command-line tool that checks an AWS account for two common issues: EC2 instances left running (costing money unnecessarily) and S3 buckets that are publicly accessible (a security risk).

## What it does

- **EC2 check** — lists all EC2 instances in the account and reports their state (running/stopped), flagging running instances as worth reviewing.
- **S3 check** — lists all S3 buckets and inspects each bucket's access control list (ACL) to flag any bucket with a public grant (i.e. accessible to "AllUsers" rather than a specific AWS account).

Both checks are read-only — the script only reports, it doesn't change anything in the AWS account.

## Example output

```
i-0350a41dd85f93b3a stopped
zohanbucket
PRIVATE
```

## Tech stack

- **Python 3**
- **boto3** — AWS's official Python SDK, used to query EC2 and S3 via the AWS API
- **AWS CLI** — used locally for authentication (boto3 reads the same credentials)

## Why I built this

I wanted hands-on practice with AWS APIs and Python while working towards an AWS Cloud Practitioner certification. Rather than just reading about EC2 and S3, this was a way to actually query a real AWS account, see the raw data AWS returns, and build logic around it — including working through nested dictionaries, understanding the difference between boto3's `client` and `resource` interfaces, and learning how AWS represents access permissions under the hood.

## Status

Working and complete for its current scope. Possible future additions:

- [ ] Check S3 bucket policies in addition to ACLs (some public buckets are made public via policy rather than ACL)
- [ ] Export results to a CSV report instead of just printing to terminal
- [ ] Add cost estimation for running EC2 instances
- [ ] Optional flag-and-fix mode (e.g. stop idle instances) currently intentionally left as read-only/reporting only

## Running it

Requires an AWS account with credentials configured locally (e.g. via `aws configure`).

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install boto3
python3 auditor.py
```
