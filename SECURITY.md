# 🔒 Security Policy

## Reporting a vulnerability

Please report vulnerabilities privately via
[GitHub Security Advisories](https://github.com/CaputoDavide93/Jamf-WakeUp-Call/security/advisories/new)
rather than opening a public issue. You should get a response within a week.

> This repository is superseded by [Jamf-SnipeIT-Suite](https://github.com/CaputoDavide93/Jamf-SnipeIT-Suite) and receives fixes only.

## Data handling

- The script reads Jamf Pro computer records (computer ID, name, serial number) for the targeted group, serial or file, and sends management-framework redeploy commands for them.
- It talks only to the Jamf Pro instance set in `JAMF_PRO_URL` (use an `https://` URL); there are no other third parties and nothing is stored beyond the log file.
- The log file (`LOG_FILE`, default `jamf_wakeup.log`) records computer IDs and serial numbers — treat it as internal data. It is git-ignored.
- Credentials (`JAMF_PRO_API_TOKEN`, or `JAMF_PRO_USERNAME` / `JAMF_PRO_PASSWORD`) are read from the environment / a local `.env` file — never committed or echoed. `.env` is git-ignored.

## Deployment checklist

- Use a dedicated Jamf Pro API account or token with only the privileges needed to read computers and computer groups and to redeploy the management framework.
- Run with `--dry-run` first to confirm the targets before sending commands.
- Keep `.env` and the log file readable only by the operator.

## Supported versions

Only the latest commit on `main` is supported.
