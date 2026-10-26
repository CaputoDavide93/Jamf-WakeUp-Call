# How it works

The tool is a thin client for two Jamf Pro APIs. It finds computers, then asks Jamf Pro to redeploy the Jamf management framework on each one. It never contacts a Mac.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/architecture-dark.svg">
  <img src="assets/architecture-light.svg" width="100%"
       alt="The operator runs the wake-up CLI; the CLI reads .env, reads computer records from Jamf Pro and posts one management-framework redeploy per computer, which Jamf Pro delivers to the Mac as an MDM command over APNs.">
</picture>

## Authentication

With `JAMF_PRO_API_TOKEN` set, the tool sends it as a bearer token on every request. With a username and password it posts them (HTTP Basic) to `/api/v1/auth/token`, and falls back to `/api/auth/tokens` and then `/uapi/auth/tokens` if the first does not return a token. The token is renewed 30 seconds before it expires. If no endpoint returns one, the run stops with "Failed to obtain Jamf API token".

## Finding computers

| Mode | Call |
|---|---|
| Group | `GET /JSSResource/computergroups/id/{group_id}`, then `GET /JSSResource/computers/id/{id}` for each member to read user details |
| Single and file | `GET /JSSResource/computers/serialnumber/{serial}` per serial |

If the detail call for one group member fails, the tool logs a warning and keeps that member with the limited record it already has.

## Sending the command

For each computer the tool sends `POST /api/v1/jamf-management-framework/redeploy/{computer_id}`. Jamf Pro answers with a device ID and a command UUID, which the tool prints. That is a queued MDM command: Jamf Pro delivers it to the Mac over Apple's push service the next time the Mac can receive it, and the Mac then reinstalls the framework.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/wake-sequence-dark.svg">
  <img src="assets/wake-sequence-light.svg" width="100%"
       alt="Sequence of one wake-up: the CLI gets a bearer token unless an API token is set, fetches the records, asks the operator to confirm, then posts one redeploy per computer unless --dry-run is set; Jamf Pro sends the MDM command over APNs and the Mac reinstalls the Jamf framework.">
</picture>

## Retries and safety

- Reads (the `GET` calls) retry up to 3 times with exponential backoff on `429`, `500`, `502`, `503` and `504`. The retry rules are mounted for HTTPS URLs only.
- The redeploy `POST` is never retried. A failure is reported and the run moves on, so one flaky response cannot queue the same command twice.
- A confirmation prompt follows the target list in every mode, unless `--skip-confirmation` is set. `--dry-run` stops after that point and sends nothing.

## What a result means

`Computer 101 (UUID: ...)` means Jamf Pro accepted the command. It does not mean the Mac has run it. A failure line carries the error Jamf Pro or the network returned.

## About the screenshots

The screenshots under `docs/assets/screenshots/` come from `make screenshots`. That script starts `tools/screenshots/mock_jamf.py`, a small local stand-in that answers the paths above with made-up computers (`demo-mac-01` and so on, serials `DEMO0000101` and so on). It runs the real CLI against it, trims the timestamp from each log line so a retake looks the same, and renders the output as a terminal window in light and dark. The mock follows the documented response shapes. It is not a Jamf Pro emulator and says nothing about how a live tenant behaves.
