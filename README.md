# cintel-04-rolling-monitoring-custom
[![Python 3.14](https://img.shields.io/badge/python-3.14%2B-blue?logo=python)](pyproject.toml)
[![CI](https://github.com/dstringer03/cintel-04-rolling-monitoring-custom/actions/workflows/ci-python-zensical.yml/badge.svg)](https://github.com/dstringer03/cintel-04-rolling-monitoring-custom/actions/workflows/ci-python-zensical.yml)
[![Documentation](https://img.shields.io/badge/docs-site-blue?logo=github)](https://dstringer03.github.io/cintel-04-rolling-monitoring-custom/)

[![uv managed](https://img.shields.io/badge/uv-managed-DE5FE9)](https://docs.astral.sh/uv/)
[![ty type checked](https://img.shields.io/badge/ty-type_checked-2F80ED)](https://docs.astral.sh/ty/)
[![Zensical docs](https://img.shields.io/badge/Zensical-docs-purple)](https://zensical.org/)
[![MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

> Monitor time-series measurements using rolling statistics.

## Project Overview

Author: Darrion Maurice Stringer

Date: 2026-11

Based on the example project by Denise Case.

I am learning how rolling averages reveal changes in system activity over time. I plan to compare different window sizes and explore how they help identify changes in reliability.

## Data

The example uses time-series system metrics from `data/`.

Each observation includes:

- `timestamp` - time of observation.
- `requests` - number of requests handled.
- `errors` - number of failed requests.
- `total_latency_ms` - total response time in milliseconds.

## Approach

The pipeline uses Polars to:

1. Read and order observations by timestamp.
2. Calculate rolling averages over a defined window.
3. Save the monitoring results for interpretation.

Explore these project components:

- [pyproject.toml](pyproject.toml) - project configuration and dependencies.
- [src/cintel/rolling_monitor.py](src/cintel/rolling_monitor.py) - rolling monitoring pipeline.
- [data/](data/) - time-series data.
- [artifacts/](artifacts/) - generated monitoring results.
- [tests/](tests/) - automated tests.
- [.github/workflows/](.github/workflows/) - automated checks and documentation deployment.
- [docs/](docs/) - project documentation.

## Run the Project

Follow the [Professional Python Workflow Guide](https://denisecase.github.io/pro-analytics-02/)
to set up your machine and project environment.

From a VS Code terminal in the project root:

```shell
uv run python -m cintel.rolling_monitor
```

## Run the Reactive App

From a VS Code terminal in the project root
(hit CTRL + c to quit):

```shell
uv run marimo run  src/cintel/app.py
```

## Results

The pipeline calculates rolling averages and writes
`artifacts/rolling_metrics.csv`.
Review the rolling measurements to understand
how smoothing can reveal trends and reduce short-term variation.

Successful execution produces a terminal message:

```shell
========================
Pipeline executed successfully!
========================
```

A `project.log` file is created in the project root.

This confirms that the Python pipeline executes
and the logging system works.

## Verification

Run the automated tests:

```shell
uv run pytest
```

## Project Documentation

The [hosted documentation site](https://dstringer03.github.io/cintel-04-rolling-monitoring-custom/)
is published using Zensical and GitHub Pages.

The documentation site is used to present the project report,
covering such sections as data, methods, results, visualizations,
interpretation, and conclusions.

## CI/CD and GitHub Actions

This project includes continuous integration and continuous deployment (CI/CD)
to check project files and publish the docs.
GitHub Actions include:

- [CI: Python and Documentation Checks](https://github.com/dstringer03/cintel-04-rolling-monitoring-custom/actions/workflows/ci-python-zensical.yml)
- [CD: Documentation Deployment](https://github.com/dstringer03/cintel-04-rolling-monitoring-custom/actions/workflows/deploy-zensical.yml)

## Developer Reference

Follow the
[Professional Python Workflow Guide](https://denisecase.github.io/pro-analytics-02/)
for **detailed instructions and troubleshooting**.

### Initialize and Update the Python Environment

With the project open in VS Code, open a VS Code terminal.
Paste each command and hit Enter or Return after to run it.

```shell
uvx pup-clean --delete
uv self update
uv python pin 3.14
uv python install
uv lock --upgrade
uv sync
uv audit
```

### Set Up and Run Git Hooks

Set up and run the git hooks to perform
basic checks automatically before
any changes get pushed to GitHub.

In the VS Code terminal,
paste each command and hit Enter or Return after to run it.

```shell
uvx prek install --force
uvx prek update --freeze --cooldown-days 7

git add -A
uvx prek run --all-files
# repeat if changes were made
uvx prek run --all-files
```

### Run Common Chores

Run linters, formatters, type checks, tests, and
build the documentation.

```shell
uv run ruff check . --fix
uv run ruff format .

uv run ty check
uv run python -m pytest
uv run python -m zensical build
```

### Git add-commit-push to GitHub

After making useful changes, save your work to GitHub.

```shell
git add -A
git commit -m "describe your changes in quotes"
git push -u origin main
```

## Developer Notes

- Use the **UP ARROW** and **DOWN ARROW** in the terminal to scroll through past commands.
- Use `CTRL+f` to find (and replace) text within a file.

## Developer Tools

This project uses professional Python tools to support development,
testing, documentation, and code quality.

- [uv](https://docs.astral.sh/uv/) - Python environments and dependencies.
- [Ruff](https://docs.astral.sh/ruff/) - Python linting and formatting, configured in [.ruff.toml](.ruff.toml).
- [ty](https://docs.astral.sh/ty/) - Python type checking.
- [pytest](https://docs.pytest.org/) - automated Python testing, configured in [.pytest.toml](.pytest.toml).
- [prek](https://prek.j178.dev/) - Git hooks and automated checks, configured in [prek.toml](prek.toml).
- [Zensical](https://zensical.org/) - project documentation, configured in [zensical.toml](zensical.toml).

## Links

- [Hosted Documentation](https://dstringer03.github.io/cintel-04-rolling-monitoring-custom/)
- [Professional Python Workflow Guide](https://denisecase.github.io/pro-analytics-02/)
- [Citation](CITATION.cff)
- [License](LICENSE)

## D2 Experiment: Comparing Window Sizes

I changed WINDOW_SIZE from 3 to 5 to see how more observations affect the rolling averages.

Prediction: I expected the larger window to smooth short-term changes more, respond more slowly, and leave the first four rows without rolling averages.

Actual results: The pipeline processed all 60 records successfully. The window of 3 had two initial rows without rolling averages. The window of 5 had four.

At 08:20, the rolling request average was 165 with a window of 3 and 150 with a window of 5. Earlier, lower request counts caused the larger window to reflect the increase more slowly.

I learned that choosing a window size involves balancing responsiveness and smoothing.

Comparison files:
- artifacts/rolling_metrics_window3.csv
- artifacts/rolling_metrics_window5.csv
