---
name: evm-mint-watcher
description: "Monitor any EVM chain (via JSON-RPC) for newly deployed ERC-721 contracts that offer a FREE mint, with anti-scam filtering, and alert via Telegram. Use when the user wants to track free mints / new NFT drops on a specific chain (e.g. Robinhood 4663, Base, etc). Pure RPC — no explorer API needed."
version: 1.0.0
author: Community
license: MIT
platforms: [linux, macos, windows]
tags: [general]
---

# Evm Mint Watcher — Skill

Monitor any EVM chain (via JSON-RPC) for newly deployed ERC-721 contracts that offer a FREE mint, with anti-scam filtering, and alert via Telegram. Use when the user wants to track free mints / new NFT drops on a specific chain (e.g. Robinhood 4663, Base, etc). Pure RPC — no explorer API needed.

## Install

```bash
cp -r <skill-name> ~/.hermes/skills/<skill-path>/
```

Or clone this repository:

```bash
git clone https://github.com/iizcm/evm-mint-watcher-skill.git ~/.hermes/skills/<skill-path>/
```

## Usage

Invoke your AI agent with a clear instruction matching this skill's purpose. The agent will route tasks to this skill when the instruction matches its description or trigger keywords.

Refer to `README.md` in this repository for:
- Detailed step-by-step installation guide
- Bilingual documentation (English + Indonesian)
- Troubleshooting table
- Security best practices
- Customization tips

## Safety rules

- Never commit private keys, seed phrases, API tokens, or personal data to version control
- Use placeholders (`<YOUR_...>`) in all examples and code snippets
- Validate all outputs before acting on them
- Keep real credentials in your runtime's secure credential store only
