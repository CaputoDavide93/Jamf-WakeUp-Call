# Configuration

The tool reads its settings from environment variables, and from a `.env` file in the directory you run it from. Copy `.env.example` to `.env` to start. `.env` is git-ignored.

| Variable | Required | Default | Description |
|---|---|---|---|
| `JAMF_PRO_URL` | Yes | none | Base URL of your Jamf Pro server, for example `https://jamf.example.com`. The tool exits if it is unset |
| `JAMF_PRO_API_TOKEN` | One of the two auth options | none | A bearer token. If set, the tool uses it as is and never asks for another |
| `JAMF_PRO_USERNAME` | One of the two auth options | none | Username for token authentication. Needs the password too |
| `JAMF_PRO_PASSWORD` | One of the two auth options | none | Password for the username above |
| `JAMF_DYNAMIC_GROUP_ID` | No | empty | Group used in group mode when you do not pass `--group-id` |
| `LOG_LEVEL` | No | `INFO` | `DEBUG`, `INFO`, `WARNING` or `ERROR` |
| `LOG_FILE` | No | `jamf_wakeup.log` | Log file path, appended to on every run |
| `API_TIMEOUT` | No | `30` | Seconds to wait for each API request |

## Authentication

Provide either `JAMF_PRO_API_TOKEN`, or both `JAMF_PRO_USERNAME` and `JAMF_PRO_PASSWORD`. With a username and password the tool requests a token from Jamf Pro and requests a new one shortly before it expires. A static token is assumed never to expire; replace it yourself when Jamf Pro retires it.

## Placeholders count as unset

`JAMF_PRO_URL`, `JAMF_PRO_API_TOKEN`, `JAMF_PRO_USERNAME` and `JAMF_PRO_PASSWORD` that start with `your_`, `your-`, `dev_` or `https://your-` are treated as missing. A copied `.env.example` therefore stops with a clear message and never contacts a made-up server.

## Use HTTPS

Point `JAMF_PRO_URL` at an `https://` address. Read-request retries are only set up for HTTPS, and credentials should not cross the network in clear text.
