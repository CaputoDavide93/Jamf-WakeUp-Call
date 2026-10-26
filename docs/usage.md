# Usage

Run every command from the repository root. The code is the `src` package, so the tool starts with `python3 -m src.main`. Without `--dry-run` it sends real commands to Jamf Pro.

## The three modes

| Mode | Command | Targets |
|---|---|---|
| Group | `python3 -m src.main` or `python3 -m src.main --group-id 42` | Every computer in a dynamic group (the group in `JAMF_DYNAMIC_GROUP_ID`, or the one you pass) |
| Single | `python3 -m src.main C02EXAMPLE001` | One computer, found by serial number |
| File | `python3 -m src.main --file computers.txt` | Every serial number in a file |

If you give `--file`, file mode wins. Otherwise a serial number selects single mode, and with neither the tool uses group mode. `--group-id` is ignored when you pass a serial number.

## Options

```
usage: python -m src.main [-h] [--file FILE] [--group-id GROUP_ID] [--dry-run]
                          [--stop-on-error] [--skip-confirmation]
                          [serial]

positional arguments:
  serial               Computer serial number to target (e.g., C02EXAMPLE001).
                       If omitted, uses dynamic group from config.

options:
  -h, --help           show this help message and exit
  --file, -f FILE      File containing serial numbers (one per line)
  --group-id GROUP_ID  Dynamic group ID (overrides config)
  --dry-run            Show what would be done without sending commands
  --stop-on-error      Stop processing if an error occurs (group mode only)
  --skip-confirmation  Skip user confirmation prompt (use with caution)
```

## Dry run and confirmation

`--dry-run` sends nothing. It does not skip the prompt: every mode asks `Do you want to proceed? (yes/no)` after listing the targets, before the dry-run step. Add `--skip-confirmation` to a dry run to read the list without answering.

```bash
python3 -m src.main --file computers.txt --dry-run --skip-confirmation
```

## The serial file

```text
# Team A
C02EXAMPLE001
C02EXAMPLE002

# Team B
C02EXAMPLE003
```

- One serial number per line.
- Lines that start with `#` are comments.
- Empty lines are ignored.
- A comment must start at the first character of the line.
- A serial Jamf Pro does not know is listed in a warning and skipped. If none are found, the run fails.

## Results and exit codes

| Exit code | Meaning |
|---|---|
| `0` | Every targeted computer was sent a command, the dry run finished, you answered `no`, or the group or file held no computers |
| `1` | A configuration error, a lookup error, or at least one computer failed |

A successful run prints `Computer <id> (UUID: ...)` per computer. A failure prints `Computer <id>: <error>` and the run continues with the next computer, unless you passed `--stop-on-error` in group mode. `--stop-on-error` has no effect in single or file mode.

## Example output

<details>
<summary>One computer</summary>

```text
====================================================================================================
WAKE-UP COMMAND SENT
====================================================================================================
✓ Computer 101 (None)
  Device ID: 101
  Command UUID: 00000000-0000-0000-0000-000000000101
====================================================================================================
```

The `(None)` is the computer name, which single mode currently reads from the wrong place in the record. It does not affect which computer is woken. See [troubleshooting](troubleshooting.md#the-computer-list-shows-n-a-and-unknown).

</details>

<details>
<summary>A batch with one failure</summary>

```text
====================================================================================================
WAKE-UP CAMPAIGN RESULTS
====================================================================================================
Total computers: 4
Successful: 3
Failed: 1
====================================================================================================

⚠️  Some computers failed to receive wake-up call:
  ✗ Computer 103: 500 Server Error: Internal Server Error for url: ...
✓ Successfully sent wake-up commands to:
  ✓ Computer 101 (UUID: 00000000-0000-0000-0000-000000000101)
  ✓ Computer 102 (UUID: 00000000-0000-0000-0000-000000000102)
  ✓ Computer 104 (UUID: 00000000-0000-0000-0000-000000000104)
```

</details>

Both blocks come from the tool run against the demo mock, with the URL shortened.
