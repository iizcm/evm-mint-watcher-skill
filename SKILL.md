---
name: evm-mint-watcher
description: Monitor any EVM chain (via JSON-RPC) for newly deployed ERC-721 contracts that offer a FREE mint, with anti-scam filtering, and alert via Telegram. Use when the user wants to track free mints / new NFT drops on a specific chain (e.g. Robinhood 4663, Base, etc). Pure RPC — no explorer API needed.
license: MIT
category: web3
---

# EVM Free-Mint Watcher

Detect new NFT contracts + free mint opportunities on any EVM chain, filter out scams, alert the user.

## When to use
- "track free mint di chain X"
- "cari NFT baru yang mint gratis"
- "alert kalau ada minting baru di Robinhood"

## Technique (all via `eth_` JSON-RPC — no explorer API)
1. **Poll new blocks**: `eth_blockNumber` → iterate `bn` from `last+1` to `current`.
2. **Contract creation** = tx where `tx.to is None`. Get `eth_getTransactionReceipt` → `contractAddress`.
3. **Is ERC-721?** `eth_call` `supportsInterface(0x80ac58cd)` (selector `0x01ffc9a7` + bytes4). Returns `0x01...` → yes.
4. **Free mint probe**: for each mint selector, `eth_call` with `from: 0x0` and no value. If result is NOT a revert (`0x08c379a0` = Error(string)), the function is callable without payment → candidate free mint.
   Common mint selectors: `mint()=0x1249c58b`, `mint(uint256)=0x40d097c3`, `publicMint()=0x29d8b0e0`, `freeMint()=0xe8b0eb2e`, `claim()=0x4e71d92d`, `safeMint(address)=0x694e80c3`, `mint(uint256,uint256)=0x7d8b7a3a`.
5. **Anti-scam filters** (apply ALL, skip if any hit):
   - code contains `setApprovalForAll` (`a22cb465`) / `approve` (`095ea7b3`) / `transferFrom` (`23b872dd`) → drainer pattern → SKIP
   - `code_size < 500` bytes → proxy/junk → SKIP
   - `Transfer` events from `0x0` (topic1 = zero address) in last ~200 blocks show `< 2` unique minters → self-mint / rug → SKIP
6. **Alert**: Telegram bot `sendMessage` to `chat_id` (from `.env` TELEGRAM_BOT_TOKEN). Also append to a log file.

## MULTI-CHAIN (this session)
Run ONE script that watches several chains at once (dict of RPC + scan-URL). This user runs RBH(4663) + ETH(1) together.
- **ETH RPC that WORKS**: `https://rpc.mevblocker.io` (llamarpc / public ankr often 429/HTML → JSONDecodeError).
- Robinhood RPC: `https://rpc.mainnet.chain.robinhood.com/`.
- Wrap every `rpc()` call in try/except returning `None` — one dead RPC must NOT crash the whole loop (public RPCs intermittently return HTML/429).
- Per-chain `last` block stored in a dict; poll all chains in one loop with `time.sleep(8)`.
- OpenSea = all standard ERC-721 are auto-listed; no extra check needed. ETH alert uses `https://etherscan.io/token/<ca>`, RBH uses `https://robinscan.io/address/<ca>`.
- Working multi-chain script is at `/root/rbh_mint_tracker.py` on the VPS (already 24/7). Reference it; don't recreate from scratch.

## Pitfalls
- `eth_getLogs` with a `fromBlock/toBlock` per single block is the reliable way to count minters (one block at a time avoids range limits).
- Headless RPC on some chains (Robinhood) is fine; public RPCs may rate-limit — use the chain's own RPC.
- **Public ETH RPCs are flaky**: `eth.llamarpc.com` returned non-JSON (HTTP 429) → `JSONDecodeError`. Use `rpc.mevblocker.io` or the chain's official RPC. Always guard `rpc()` with try/except.
- "Free" via `eth_call` is a heuristic: a contract can still charge in `mintTo` or require holding another token. Always tell the user to verify manually before minting.
- Don't run multiple watchers against the same RPC without sleep — 8s poll is safe.
- **Don't scrape third-party freemint aggregator sites (MCT.xyz, etc.) as a substitute for this watcher.** They are Vue/React SPAs: data loads via JS/WebSocket behind login or "Gold Membership", so `curl`/static HTML returns only the nav bar, and there is no public REST endpoint (got 404 on every `/api/...` guess). The robust path is to BUILD YOUR OWN RPC watcher (this skill) covering the chains you care about. The user explicitly chose this over scraping MCT after the scrape returned only nav text.
- **Scope discipline**: this user runs RBH(4663) + ETH(1) only — when extending, ask before adding more chains (BSC/Polygon/Base/ARB). Don't assume "all chains."

## Support
- `scripts/mint_watcher.py` — runnable single-chain watcher. Usage: `python3 mint_watcher.py <RPC_URL> <CHAIN_LABEL> <TELEGRAM_CHAT_ID>`. Reads `TELEGRAM_BOT_TOKEN` from `/root/.hermes/.env`.
- Multi-chain production script: `/root/rbh_mint_tracker.py` on VPS (RBH + ETH, 24/7, alerts to chat 6207321022).
