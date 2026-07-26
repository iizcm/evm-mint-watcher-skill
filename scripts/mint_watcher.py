#!/usr/bin/env python3
# Generic EVM free-mint watcher. Usage:
#   python3 mint_watcher.py <RPC_URL> <CHAIN_LABEL> <TELEGRAM_CHAT_ID>
# Reads TELEGRAM_BOT_TOKEN from /root/.hermes/.env
import sys, time, requests

RPC = sys.argv[1]
CHAIN = sys.argv[2]
CHAT = sys.argv[3]

def env():
    d = {}
    for l in open('/root/.hermes/.env').read().split('\n'):
        if l and not l.startswith('#') and '=' in l:
            k, v = l.split('=', 1); d[k.strip()] = v.strip().strip('"').strip("'")
    return d

TOK = env().get('TELEGRAM_BOT_TOKEN', '')

def tg(m):
    try:
        requests.post(f"https://api.telegram.org/bot{TOK}/sendMessage",
                      json={"chat_id": CHAT, "text": m, "disable_web_page_preview": True}, timeout=10)
    except Exception as e:
        print(f"[tg err] {e}", flush=True)

def rpc(m, p):
    r = requests.post(RPC, json={"jsonrpc": "2.0", "method": m, "params": p, "id": 1}, timeout=15)
    return r.json().get("result")

ERC721 = "0x80ac58cd"
MINT_SEL = {"mint()": "0x1249c58b", "mint(uint256)": "0x40d097c3", "publicMint()": "0x29d8b0e0",
            "freeMint()": "0xe8b0eb2e", "claim()": "0x4e71d92d", "safeMint(address)": "0x694e80c3",
            "mint(uint256,uint256)": "0x7d8b7a3a"}
SUS = ["a22cb465", "095ea7b3", "23b872dd"]

def is_erc721(a):
    r = rpc("eth_call", [{"to": a, "data": "0x01ffc9a7" + ERC721[2:]}, "latest"])
    return r and r.startswith("0x01")

def code_size(a):
    c = rpc("eth_getCode", [a, "latest"]) or "0x"
    return len(c) - 2 if c.startswith("0x") else 0

def has_sus(a):
    c = (rpc("eth_getCode", [a, "latest"]) or "").lower()
    return any(s in c for s in SUS)

def try_free(a):
    f = []
    for n, s in MINT_SEL.items():
        try:
            r = rpc("eth_call", [{"to": a, "data": s, "from": "0x" + "0" * 40}, "latest"])
            if r is not None and not r.startswith("0x08c379a0"):
                f.append(n)
        except: pass
    return f

def mint_event_count(a, blocks=200):
    cur = int(rpc("eth_blockNumber", []), 16)
    uniq = set()
    sig = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    for bn in range(max(1, cur - blocks), cur + 1):
        try:
            logs = rpc("eth_getLogs", [{"fromBlock": hex(bn), "toBlock": hex(bn), "address": a,
                "topics": [sig, "0x" + "0" * 64]}])
            for l in logs or []:
                if len(l.get("topics", [])) > 2:
                    uniq.add(l["topics"][2])
        except: pass
    return len(uniq)

last = int(rpc("eth_blockNumber", []), 16)
print(f"[watcher {CHAIN}] start {last}", flush=True)
seen = set()
while True:
    try:
        cur = int(rpc("eth_blockNumber", []), 16)
        for bn in range(last + 1, cur + 1):
            blk = rpc("eth_getBlockByNumber", [hex(bn), True])
            if not blk:
                continue
            for tx in blk.get("transactions", []):
                if tx.get("to") is None:
                    rc = rpc("eth_getTransactionReceipt", [tx["hash"]])
                    if rc and rc.get("contractAddress"):
                        ca = rc["contractAddress"].lower()
                        if ca in seen:
                            continue
                        seen.add(ca)
                        if not is_erc721(ca):
                            continue
                        if has_sus(ca):
                            print(f"[{CHAIN}] SUS {ca}", flush=True); continue
                        if code_size(ca) < 500:
                            print(f"[{CHAIN}] SMALL {ca}", flush=True); continue
                        mints = try_free(ca)
                        if not mints:
                            continue
                        uniq = mint_event_count(ca)
                        if uniq < 2:
                            print(f"[{CHAIN}] 1MINTER {ca} uniq={uniq}", flush=True); continue
                        msg = (f"🟢 {CHAIN} FREEMINT (clean)\nContract: {ca}\nBlock: {bn}\n"
                               f"Mint: {mints}\nMinters: {uniq}\n")
                        print(msg, flush=True)
                        open("/root/mints_%s.log" % CHAIN, "a").write(msg + "\n")
                        tg(msg)
        last = cur
        time.sleep(8)
    except Exception as e:
        print(f"[err] {e}", flush=True)
        time.sleep(15)
