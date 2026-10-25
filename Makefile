# One entry point for the checks CI runs. `make check` before every push.
PYTHON := .venv/bin/python

.PHONY: venv test diagram check screenshots social-preview

venv: ## Project environment: runtime and test dependencies
	python3 -m venv .venv
	$(PYTHON) -m pip install -q -r requirements-dev.txt

test: ## The pytest suite
	$(PYTHON) -m pytest -q

diagram: ## Redraw docs/assets/*.svg
	python3 tools/gen_diagram.py

check: test ## Everything CI checks
	python3 tools/gen_diagram.py --check
	sh tools/brand/check-icon.sh

screenshots: venv ## Retake docs/assets/screenshots/ against the demo mock (not CI)
	test -x .venv-screenshots/bin/python || ( \
		python3 -m venv .venv-screenshots && \
		.venv-screenshots/bin/pip install -q -r tools/screenshots/requirements.txt )
	.venv-screenshots/bin/python -m playwright install chromium
	.venv-screenshots/bin/python tools/screenshots/take_screenshots.py

social-preview: ## Redraw docs/assets/social-preview.png (needs Google Chrome and pillow)
	python3 tools/brand/brand_kit.py social --repo Jamf-WakeUp-Call --name "Jamf WakeUp Call" --tagline "Wake the Macs that stopped checking in to Jamf Pro, by group, serial or file" --chip "Dry run first" --chip "Group, serial or file" --chip "Jamf Pro API" --icon docs/assets/brand/icon.svg
