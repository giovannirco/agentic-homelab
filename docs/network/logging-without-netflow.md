# Network logging without NetFlow: UniFi activity logs → Vector → Loki → Grafana

NetFlow/IPFIX costs gateway CPU. Most of what a home network needs (who connected, admin actions, threat detections, firewall events) is already in the controller's **activity log**, which UniFi can send as **CEF over syslog** ("SIEM Server").

**Stack (one small VM with Docker, pinned versions):**
- **Vector**: syslog listener (514 udp/tcp) + netconsole (a separate UDP port). `parse_cef()` the events. Note: RFC3164 parsing splits `CEF:0|…` into appname `CEF` + message `0|…`, so put the prefix back before parsing.
- **Loki**: storage with retention (e.g. 90 days). Use a **fixed, low-cardinality label set** (job, kind, host, category, severity, app) and keep the full event as the JSON log line (`| json` in queries).
- **Grafana**: Explore/dashboards/alerts. Add an MCP server (e.g. mcp-grafana) so an agent can query the logs.

**Options if you want more:**
| Need | Tool |
|---|---|
| Traffic stats without NetFlow | Unpoller (reads the controller API) → Prometheus/Mimir → Grafana |
| Real SIEM rules and alerts | Wazuh (own VM; its indexer needs `vm.max_map_count`) |
| Flow analytics, if you do enable NetFlow | Akvorado (ClickHouse; supports a URL prefix behind a reverse proxy) |

**Gotchas:** UniFi saves the whole Traffic Logging page at once (an empty SNMP community blocks all changes); a restricted local admin for Unpoller has to be created in the UI, not the API.

Related: [testing-and-benchmarks.md](testing-and-benchmarks.md), [network-foundation.md](network-foundation.md).
