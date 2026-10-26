# Contributing

This repository is superseded by [Jamf-Snipe-IT-Suite](https://github.com/CaputoDavide93/Jamf-Snipe-IT-Suite) and receives fixes only. Bug reports, small fixes and environment reports are welcome.

## Report an environment

The most useful report is a setup this tool has or has not worked on. Open an [environment report](https://github.com/CaputoDavide93/Jamf-WakeUp-Call/issues/new?template=environment-report.yml) and include:

- Jamf Pro version, and whether it is cloud or self-hosted.
- Python version and operating system.
- The command you ran, with serial numbers and the server URL replaced by examples.
- What you expected and what happened, including the exit code.
- The relevant lines of the log, taken with `LOG_LEVEL=DEBUG`.

Before you paste anything, remove tokens, passwords, your server URL, serial numbers, computer names and user names. Never attach your `.env` file.

## Send a fix

1. Branch from `main`.
2. Make the change and add a test where it fits.
3. Run `make venv` once, then `make check`. It runs the pytest suite, the diagram check and the icon check.
4. Open a pull request with a conventional title such as `fix: ...` or `docs: ...`.

If you change a diagram, run `python3 tools/gen_diagram.py` and commit the SVGs. If you change what the CLI prints, retake the screenshots with `make screenshots`.
