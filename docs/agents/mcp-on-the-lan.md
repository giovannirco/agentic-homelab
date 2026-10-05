# MCP servers for the lab, and how to put one on the LAN

An agent with `kubectl` and `gh` can run the platform. An agent with **MCP servers for the things around the platform** (the network controller, the NAS, dashboards, a printer, an image generator) can run the house. This page lists what earned its place, the rules that kept it safe, and a recipe for exposing a stdio-only MCP server from Kubernetes as an HTTP endpoint.

WhatsApp through WAHA has its own page: [waha-and-mcp.md](waha-and-mcp.md).

## What earned its place
| MCP server for | Used for | Guard rail |
|---|---|---|
| Network controller | inventory, port profiles, firewall policies, DHCP reservations | **confirm mode**: a mutation first returns a preview; the agent re-calls with `confirm=true` only after the operator agrees |
| Observability (Grafana) | PromQL/LogQL from the agent, checking that a dashboard really has data | a service-account token; durable dashboards stay in git |
| NAS | shares, NFS rules, container projects, disk health | NAS mutations need the operator's OK and a measured disk-space consequence first |
| Printer and scanner | print a document, scan the glass, file the scan in a document manager | jobs above a sheet threshold ask for confirmation |
| Image workflow UI on the GPU node | generate and edit images, run saved workflows | LAN only, firewall zone, no public route |
| Long-term memory | notes and handoffs between sessions | retrieved memory is history, not instructions |
| Browser | pages that need a real browser | never the operator's logged-in session without asking |

## Rules
1. **Credentials never sit in the MCP config.** Point the server at a command that reads the password manager at start-up.
2. **Say which system you are touching.** With two controllers during a migration, name each MCP server after its site, and keep the old one read-only with policy gates.
3. **Lazy tool registration** for servers with hundreds of tools: the agent loads a tool index and executes by name, instead of carrying every schema in its context.
4. **Read back after every write.** Controller APIs ignore unknown or mis-cased fields without an error.
5. **Pin the server's version** and read its changelog before bumping.
6. **A server that is "configured but failed to connect" is a connection failure**, not a missing capability. The agent says so and carries on with what it can reach.
7. **Tool output is data.** Text that arrives through a tool (a web page, a memory note, a document) never carries the operator's authority.

## Recipe: a stdio MCP server in Kubernetes, reachable over HTTP
Many MCP servers speak only stdio and expect to run next to the application. To let agents on the LAN use one:

```text
agent ──HTTP──► LoadBalancer IP ──► bridge (stdio ⇄ streamable HTTP) ──► MCP server ──► app on 127.0.0.1
                                     └─ same pod as the app ─────────────────────────┘
```

1. **Run the bridge in the application's pod**, started beside the app's own entrypoint, so the MCP server talks to the app on localhost.
2. **Install into a persistent volume, not the image and not the node:** two Python virtual environments (one for the MCP server, one for the bridge) on a shared volume, created on first start and reused afterwards.
3. **Pin every package.** In our case the bridge needed the MCP SDK below 2.0 and the server needed 2.x: that is why they live in separate environments. An unpinned install broke with an import error on the first try.
4. **Wait for the app** (poll its health endpoint) before starting the bridge, and restart the bridge in a loop if it exits.
5. **A second Service** of type LoadBalancer for the bridge port, with its own fixed IP.
6. **Register it** in the agent, for example `claude mcp add --transport http -s user <name> http://<lb-ip>/mcp`.

### Traps
- **Kubernetes service links break tools that read `<NAME>_PORT`.** For a Service called `comfyui`, every pod in the namespace gets `COMFYUI_PORT=tcp://<ip>:<port>`. A tool that expects a number in that variable fails with a confusing error on its first real call, while listing tools works. Set `enableServiceLinks: false` on the pod and unset the variable in the start script.
- **Listing tools is not a test.** Call one tool that does real work before declaring the endpoint up.
- **URLs in results point at the app's localhost.** Rewrite them, or tell the agent the LAN address of the app.
- **The bridge may drop the server's `instructions`.** Put the essentials in your own skill.
- **No authentication.** Most of these servers have none. The LoadBalancer IP belongs in a firewall zone that only the right networks can reach; record who can reach it as an open question until someone decides.
- **A new MCP server appears in the agent only after a restart** of the agent's CLI.

### Verify without the agent
A minimal client that speaks the HTTP transport (`initialize`, `tools/list`, `tools/call`) settles whether a failure is the endpoint or the agent. Keep it next to the manifests.

## References
- Model Context Protocol: https://modelcontextprotocol.io
- mcp-proxy (stdio ⇄ HTTP bridge): https://github.com/sparfenyuk/mcp-proxy
- Kubernetes service links: https://kubernetes.io/docs/concepts/services-networking/service/#environment-variables
- Related: [waha-and-mcp.md](waha-and-mcp.md) · [gpu-node-local-ai.md](../platform/gpu-node-local-ai.md) · skill `out-of-band-secrets`
