# Troubleshooting

Find your symptom, then follow the fix. Set `LOG_LEVEL=DEBUG` in `.env` and read the file named by `LOG_FILE` (default `jamf_wakeup.log`) when the symptom does not say enough.

## The tool says JAMF_PRO_URL is not configured

The variable is unset, empty, or still the `.env.example` placeholder. Edit `.env` and set your real server URL. Run from the repository root, because `.env` is read from the current directory.

## It says no authentication method is configured

Set `JAMF_PRO_API_TOKEN`, or set both `JAMF_PRO_USERNAME` and `JAMF_PRO_PASSWORD`. Values that still start with `your_` count as unset.

## 401 Unauthorized, or "Failed to obtain Jamf API token"

- Check the credentials in `.env`.
- Confirm the account has API access and is not locked or disabled.
- With an API token, check it has not expired or been revoked.
- Try the same account against the Jamf Pro API directly to rule out the tool.

## 403 Forbidden

The account authenticates but lacks a privilege. Give it read access to computers and computer groups and the permission to send the management framework redeploy command. Exact privilege names are unverified here; the Jamf Pro audit log or the response body names the missing one.

## Computer not found

- Check the serial number for typos. Jamf Pro matches the serial it has on record.
- Confirm the computer is enrolled in Jamf Pro.
- In file mode, unknown serials are listed and skipped; the run fails only if none are found.

## Connection refused, timeout, or SSL error

- Check `JAMF_PRO_URL` is correct, includes `https://`, and has no trailing path.
- Check your network and any proxy or firewall between you and the server.
- Raise `API_TIMEOUT` if the server is slow.

## 429 Too Many Requests or 5xx errors

Reads retry 3 times with backoff over HTTPS. If a run still fails, wait a few minutes and run again. A failed redeploy is never retried automatically, so re-run only the computers listed as failed (put their serials in a file and use `--file`).

## --dry-run still asks yes or no

That is how the tool works: the prompt comes before the dry-run step in every mode. Answer `yes` to see the preview, or add `--skip-confirmation`. Nothing is sent either way.

## The computer list shows N/A and Unknown

Run against the demo mock, which follows the Jamf Pro Classic API record shape (`general.id`, `general.name`), the confirmation list and the dry-run lines print `[ N/A] Unknown`, and single mode prints `Computer 101 (None)`. The code reads `id` and `name` from the top of the record, while that API nests them under `general`. The commands themselves use `general.id`, so the right computers are targeted. This is unverified against a live tenant. Check the target list by serial number or user, which do display, and open an [environment report](https://github.com/CaputoDavide93/Jamf-WakeUp-Call/issues/new?template=environment-report.yml) with what you see.

## Nothing happens on the Mac

A command UUID means Jamf Pro queued the command, not that the Mac ran it. The Mac must be powered on, online and able to reach Apple's push service. Check the computer's management history in Jamf Pro, and try again once the Mac is awake and on the network.

## ModuleNotFoundError: No module named 'requests'

Install the dependencies in the Python you run: `pip install -r requirements.lock.txt`. If you use a virtual environment, activate it first.

## ModuleNotFoundError: No module named 'src'

Run from the repository root with `python3 -m src.main`, not `python3 src/main.py`.
