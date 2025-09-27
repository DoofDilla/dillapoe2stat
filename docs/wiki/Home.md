# DillaPoE2Stat Wiki

Welcome to the GitHub Wiki for **DillaPoE2Stat**, the hotkey-driven Path of Exile 2 map tracker. This wiki collects module-level documentation, API call references, and operational guides so contributors can quickly understand how the project fits together.

## Quick navigation
- [Core Loop Overview](Core-Loop-Overview.md) – Understand the responsibilities of `poe_stats_refactored_v2.py` and how managers work together.
- [Module Reference](Module-Reference.md) – Browse every helper module, their public functions, and the data they expect/return.
- [External API Usage](External-API-Usage.md) – Review how we authenticate with the official Path of Exile API and consume poe.ninja economy data.
- [Maintaining the Wiki](Maintaining-the-Wiki.md) – Learn how to keep these pages in sync with the dedicated GitHub Wiki.

## How to use this wiki
Each page is written in GitHub-flavoured Markdown so it renders identically in this repository and inside the GitHub Wiki. After editing any page under `docs/wiki`, push normally—the automation described in [Maintaining the Wiki](Maintaining-the-Wiki.md) will mirror the content into the wiki repository once your pull request merges.

Looking for a quickstart on running the tracker? See the top-level [`README.md`](../README.md) for installation, configuration, and usage instructions.
