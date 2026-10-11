#!/usr/bin/env python3
"""Guardian Protectors MCP Server — XRPL Ecosystem Infrastructure
Built by Guardian Protectors (@xrplove) · Universal Standard"""

import json
import os

import requests
from fastmcp import FastMCP

XRPL_RPC = os.environ.get('XRPL_RPC', 'https://rpc.xrplclaw.com')
# Public XRPL JSON-RPC node, used if XRPL_RPC can't be reached.
XRPL_RPC_FALLBACK = os.environ.get('XRPL_RPC_FALLBACK', 'https://s1.ripple.com')
EVM_RPC = os.environ.get('EVM_RPC', 'https://rpc.xrplevm.org')
REGISTRY_ADDR = '0x5e942B11AF069Fbab93CaEce0B3FE277D7c095f6'
ORACLE_ADDR = '0x6345A654B850a95Aa489BA5034F4047Cc461fE68'

mcp = FastMCP(name="guardian-xrpl", instructions="XRPL ecosystem infrastructure")


def xrpl_rpc(method, params=None):
    """Call an XRPL JSON-RPC method, trying the fallback node if the main one fails."""
    payload = {"method": method, "params": [params or {}]}
    last_error = None
    for url in (XRPL_RPC, XRPL_RPC_FALLBACK):
        try:
            return requests.post(url, json=payload, timeout=15).json()
        except Exception as e:  # network error or bad JSON: try the next node
            last_error = e
    raise last_error


def evm_rpc(method, params=None):
    return requests.post(EVM_RPC, json={"jsonrpc": "2.0", "method": method, "params": params or [], "id": 1}, timeout=15).json()


@mcp.tool()
async def xrpl_account_info(address: str) -> str:
    resp = xrpl_rpc('account_info', {"account": address, "ledger_index": "validated"})
    if 'result' in resp and 'account_data' in resp['result']:
        acct = resp['result']['account_data']
        return json.dumps({"address": address,
                           "balance_xrp": float(acct.get('Balance', 0)) / 1_000_000,
                           "sequence": acct.get('Sequence', 0),
                           "owner_count": acct.get('OwnerCount', 0)}, indent=2)
    return json.dumps({"error": "Account not found"})


@mcp.tool()
async def xrpl_ledger_info() -> str:
    resp = xrpl_rpc('ledger', {"ledger_index": "validated"})
    if 'result' in resp:
        r = resp['result']
        return json.dumps({"ledger_index": r.get('ledger_index'),
                           "hash": r.get('ledger_hash', '')[:20] + '...'}, indent=2)
    return json.dumps({"error": "Failed"})


@mcp.tool()
async def evm_balance(address: str) -> str:
    result = evm_rpc('eth_getBalance', [address, "latest"])
    if 'result' in result:
        bal = int(result['result'], 16)
        return json.dumps({"address": address, "balance_xrp": float(bal) / 1e18, "network": "XRPL EVM"}, indent=2)
    return json.dumps({"error": "Failed"})


@mcp.tool()
async def evm_gas_price() -> str:
    result = evm_rpc('eth_gasPrice')
    if 'result' in result:
        g = int(result['result'], 16) / 1e9
        return json.dumps({"gas_price_gwei": round(g, 6)}, indent=2)
    return json.dumps({"error": "Failed"})


@mcp.tool()
async def evernode_network_stats() -> str:
    # Snapshot figures (not fetched live).
    return json.dumps({"total_hosts": 12087, "active": 5674, "idle": 6413, "idle_pct": 53.1,
                       "epoch": 5, "epoch_pool_evr": 3744747.49, "rep_threshold": 200}, indent=2)


@mcp.tool()
async def bridge_health_check() -> str:
    checks, alerts = [], []
    try:
        r = xrpl_rpc('ledger', {"ledger_index": "validated"})
        li = r.get('result', {}).get('ledger_index')
        checks.append({"component": "XRPL", "status": "ok", "ledger": li})
    except Exception as e:
        checks.append({"component": "XRPL", "status": "error"})
        alerts.append("XRPL unreachable")
    try:
        b = evm_rpc('eth_blockNumber')
        bn = int(b['result'], 16)
        checks.append({"component": "EVM", "status": "ok", "block": bn})
    except Exception as e:
        checks.append({"component": "EVM", "status": "error"})
        alerts.append("EVM unreachable")
    overall = "ALL CLEAR" if not alerts else f"{len(alerts)} ALERTS"
    return json.dumps({"status": overall, "checks": checks, "alerts": alerts}, indent=2)


@mcp.tool()
async def guardian_overview() -> str:
    return json.dumps({"project": "Guardian Protocols", "operator": "@xrplove", "company": "Universal Standard",
                       "testnet_contracts": {"CrossLayerRegistry": REGISTRY_ADDR, "EvernodeHostOracle": ORACLE_ADDR},
                       "mainnet_contracts": "AWAITING DEPLOYMENT", "github": "https://github.com/xrplove"}, indent=2)


if __name__ == '__main__':
    import sys
    # stdout carries the MCP protocol, so the greeting goes to stderr.
    print("Guardian XRPL MCP Server - @xrplove", file=sys.stderr)
    mcp.run(transport='stdio')
