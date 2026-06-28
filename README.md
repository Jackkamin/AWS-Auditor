# AWS Account Auditor

A Python command-line tool that checks an AWS account for common cost and security issues: EC2 instances left stopped (and still costing money via attached storage), S3 buckets that are publicly accessible, and IAM users with stale access keys or no MFA enabled.

## What it does

- **EC2 check** — flags any stopped instance as worth reviewing. A stopped instance isn't running, but any EBS volume still attached to it keeps costing money every month until someone notices and cleans it up.
- **S3 check** — inspects each bucket's access control list (ACL) and flags any bucket with a public grant (i.e. accessible to "AllUsers" rather than a specific AWS account).
- **IAM check** — for each IAM user:
  - Flags any access key older than 30 days as due for review (basic key-rotation hygiene).
  - Flags any user with no MFA device registered as a security risk.

All checks are read-only — the script only reports, it doesn't change anything in the AWS account.
I do plan on making a tool to actually make changes on AWS but no planned date.

## Example output

```
instance i-0350a41dd85f93b3a Server is currently stopped, do you still need this server? HIGH
Bucket zohanbucket Bucket is publicly accessible HIGH
User jackkamin - Key AKIAUTMLXXVSXDPZONNR Access key is 45 days old MEDIUM
User jackkamin MFA is not enabled HIGH
```

## Tech stack

- **Python 3**
- **boto3** — AWS's official Python SDK, used to query EC2, S3, and IAM via the AWS API
- **AWS CLI** — used locally for authentication (boto3 reads the same credentials)

## Why I built this

I wanted hands-on practice with AWS APIs and Python while working towards an AWS Cloud Practitioner certification. Rather than just reading about EC2, S3, and IAM, this was a way to actually query a real AWS account, see the raw data AWS returns, and build logic around it — including working through nested dictionaries, the difference between boto3's `client` and `resource` interfaces, how AWS represents access permissions, and handling date/time comparisons across timezone-aware and naive Python objects.

Along the way I found and fixed a couple of real logic bugs rather than just writing the "happy path":

- An early version of the S3 check printed a verdict per ACL grant rather than per bucket, so a bucket with multiple grants could print contradictory "PUBLIC" and "PRIVATE" lines for itself. Fixed by tracking a single flag across all grants for a bucket before deciding on one final verdict.
- The original version of every check printed results directly as it found them, mixing "deciding something is a problem" with "displaying it to a user." This meant nothing was reusable — no way to sort by severity, generate a report, or test the logic without it printing to a terminal. Refactored every check to build a list of structured findings (`{resource, issue, severity}`) and `return` them, with `main()` deciding how to display the results. This also surfaced a real bug during the refactor: a misplaced `return` inside a loop that would have silently skipped checking every user after the first MFA failure.

## Status

Working and complete for its current scope (EC2 stopped-instance check, S3 public bucket check, IAM key age and MFA checks). All checks return structured findings rather than printing directly, which the next set of features build on. Possible future additions:

- [ ] Check S3 bucket policies in addition to ACLs (some public buckets are made public via policy rather than ACL, and policy-based exposure is the more common real-world cause now)
- [ ] Sort/filter output by severity instead of printing in discovery order
- [ ] Export results to a CSV or HTML report instead of just printing to terminal
- [ ] Add cost estimation for flagged EC2 instances and their attached storage
- [ ] Make thresholds (key age, etc.) configurable instead of hardcoded
- [ ] Error handling so one missing permission or malformed response doesn't crash the whole run
- [ ] Optional flag-and-fix mode (e.g. stop idle instances) — currently intentionally left as read-only/reporting only

## Running it

Requires an AWS account with credentials configured locally (e.g. via `aws configure`).

```
python3 -m venv venv
source venv/bin/activate
pip3 install boto3
python3 auditor.py
```
