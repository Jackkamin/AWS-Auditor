# AWS Account Auditor

A Python command-line tool that checks an AWS account for common cost and security issues: EC2 instances left running, S3 buckets that are publicly accessible, and IAM users with stale access keys or no MFA enabled.

## What it does

- **EC2 check** — lists all EC2 instances in the account and reports their state (running/stopped), flagging running instances as worth reviewing.
- **S3 check** — lists all S3 buckets and inspects each bucket's access control list (ACL) to flag any bucket with a public grant (i.e. accessible to "AllUsers" rather than a specific AWS account).
- **IAM check** — for each IAM user:
  - Calculates the age of each access key and flags any older than 30 days as due for review (a basic key-rotation hygiene check).
  - Checks whether the user has any MFA device registered, flagging accounts with no MFA as a security risk.

All checks are read-only — the script only reports, it doesn't change anything in the AWS account.

## Example output

```
i-0350a41dd85f93b3a stopped
zohanbucket Is False

 IAM Checks:

User Name: jackkamin
User ID: AIDAUTMLXXVS57J7UK457
Password last used: 2026-06-23 23:05:34+00:00
Key ID: AKIAUTMLXXVSXDPZONNR
Creation Date: 2026-05-10 10:24:49+00:00
This IAM User is: 45 days old.
FLAGGED FOR REVIEW!
List is empty, REVIEW
```

## Tech stack

- **Python 3**
- **boto3** — AWS's official Python SDK, used to query EC2, S3, and IAM via the AWS API
- **AWS CLI** — used locally for authentication (boto3 reads the same credentials)

## Why I built this

I wanted hands-on practice with AWS APIs and Python while working towards an AWS Cloud Practitioner certification. Rather than just reading about EC2, S3, and IAM, this was a way to actually query a real AWS account, see the raw data AWS returns, and build logic around it — including working through nested dictionaries, the difference between boto3's `client` and `resource` interfaces, how AWS represents access permissions, and handling date/time comparisons across timezone-aware and naive Python objects.

Along the way I found and fixed a real logic bug: an early version of the S3 public-access check printed a verdict per ACL grant rather than per bucket, meaning a bucket with multiple grants could print contradictory "PUBLIC" and "PRIVATE" lines for itself. Fixed by tracking a single flag across all grants for a bucket before printing one final verdict.

## Status

Working and complete for its current scope (EC2, S3, IAM key age, IAM MFA). Possible future additions:

- [ ] Check S3 bucket policies in addition to ACLs (some public buckets are made public via policy rather than ACL)
- [ ] Export results to a CSV report instead of just printing to terminal
- [ ] Add cost estimation for running EC2 instances
- [ ] Make the key-age and review thresholds configurable instead of hardcoded
- [ ] Optional flag-and-fix mode (e.g. stop idle instances) — currently intentionally left as read-only/reporting only

## Running it

Requires an AWS account with credentials configured locally (e.g. via `aws configure`).

```bash
python3 -m venv venv
source venv/bin/activate
pip3 install boto3
python3 auditor.py
```
