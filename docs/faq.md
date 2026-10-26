# FAQ

## What does Jamf WakeUp Call do?

It asks Jamf Pro to redeploy the Jamf management framework on the Macs you choose, by dynamic group, serial number or a file of serials. Jamf Pro then delivers an MDM command to each Mac. The tool never connects to a Mac itself.

## Is it safe to run on production Macs?

Start with `--dry-run` and one serial number you can watch, then widen. The tool sends one redeploy command per computer, never retries it, and asks for confirmation unless you pass `--skip-confirmation`. It is provided as is; test in a non-production setup first.

## Does `--dry-run` send anything?

No. It lists what would be sent and stops. It still asks yes or no first unless you add `--skip-confirmation`.

## Which Jamf Pro versions does it support?

Unknown. No version has been recorded, and the tests run against a local mock, not a live server. The tool uses the Jamf Pro Classic API for lookups and the Jamf Pro API for the redeploy call.

## How do I log in: token or password?

Either. Set `JAMF_PRO_API_TOKEN`, or set `JAMF_PRO_USERNAME` and `JAMF_PRO_PASSWORD`. With a username and password the tool fetches a token and renews it before it expires.

## What privileges does the account need?

Read access to computers and computer groups, plus permission to send the management framework redeploy command. Use a dedicated account with nothing more. The exact privilege names are unverified here.

## How do I wake many Macs at once?

Put their serial numbers in a text file, one per line, and run `python3 -m src.main --file computers.txt`. Or point `--group-id` at a dynamic group that matches them.

## Why did a command succeed but the Mac did nothing?

A success means Jamf Pro accepted and queued the command. The Mac acts on it when it is on, online and able to reach Apple's push service.

## Can I run it on a schedule?

Yes, with `--skip-confirmation`. Run `--dry-run --skip-confirmation` by hand first and read the target list. Nothing in the tool limits how often it runs, so choose a sensible interval.

## Does it store my credentials or data?

Credentials are read from the environment or a local `.env` and are not written anywhere by the tool. The log file records computer IDs and serial numbers; it is git-ignored. See [SECURITY.md](../SECURITY.md).

## Why is this repository superseded?

The same logic moved into [Jamf-SnipeIT-Suite](https://github.com/CaputoDavide93/Jamf-SnipeIT-Suite) as its `wakeup` module, with retries and SSM-backed credentials. This repo stays for reference and receives fixes only.

## How do I report that it works, or does not, on my setup?

Open an [environment report](https://github.com/CaputoDavide93/Jamf-WakeUp-Call/issues/new?template=environment-report.yml). [CONTRIBUTING.md](../CONTRIBUTING.md) lists what to attach and what to remove first.
