# Guardian XRPL MCP Server

A small [MCP](https://modelcontextprotocol.io) server by Guardian Protectors (@xrplove) · Universal Standard.
It lets an AI assistant (Claude Desktop, Cursor, and others) look up live, read-only data from the XRP Ledger and the XRPL EVM sidechain.
It never asks for or uses keys, seeds, or wallets.

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python mcp_server.py
```

The server talks over stdio, so it is normally started by an MCP client. Example client config:

```json
{
  "mcpServers": {
    "guardian-xrpl": {
      "command": "/path/to/.venv/bin/python",
      "args": ["/path/to/mcp_server.py"]
    }
  }
}
```

## Tools

| Tool | What it does |
| --- | --- |
| `xrpl_account_info(address)` | Balance (XRP), sequence and owner count for an XRPL account |
| `xrpl_ledger_info()` | Latest validated ledger index and hash |
| `evm_balance(address)` | Balance of an address on the XRPL EVM sidechain |
| `evm_gas_price()` | Current XRPL EVM gas price in gwei |
| `evernode_network_stats()` | Evernode host network snapshot (fixed figures, not live) |
| `bridge_health_check()` | Checks that both the XRPL and XRPL EVM nodes answer |
| `guardian_overview()` | Project info and testnet contract addresses |

## Servers

| Setting | Default | Notes |
| --- | --- | --- |
| `XRPL_RPC` | `https://rpc.xrplclaw.com` | Main XRPL JSON-RPC node |
| `XRPL_RPC_FALLBACK` | `https://s1.ripple.com` | Public Ripple node, used if the main one can't be reached |
| `EVM_RPC` | `https://rpc.xrplevm.org` | XRPL EVM JSON-RPC node |

Override any of them with an environment variable of the same name.

## Related

- [HCN Network Dashboard](https://xrplove.github.io/hcn-network-dashboard/): live, read-only XRP Ledger dashboard

## License

[MIT](LICENSE)
