# Português (resumo)

Caminho **homelab + agentes de IA → engenharia de plataforma**.

1. Leia [../00-philosophy.md](../00-philosophy.md) (inglês técnico).
2. Siga [../setup/](../setup/) na ordem (01 → 13).
3. Skills no Hermes: `bash scripts/install-skills.sh --hermes`
4. Issues + board como fila de trabalho.
5. Footguns: [../lessons/hard-won.md](../lessons/hard-won.md)
6. Índice: [../MAP.md](../MAP.md)

**Ideia:** Kubernetes é a estrada. GitOps, CNI, tunnel e o agente andam nela. A IA multiplica com skills e permissões certas — não com cluster-admin solto.


## Novo (2026-10): mais máquinas, GPU e agentes

- **Omni + netboot:** a máquina liga pela rede, aparece sozinha no Omni e espera um template dizer de qual cluster ela é. Veja [omni-and-netboot.md](../platform/omni-and-netboot.md).
- **IPs de LoadBalancer por L2 ou BGP**, com a queda medida em cada caso (16,5 s no L2; 2 s no BGP com os timers certos): [loadbalancer-l2-vs-bgp.md](../platform/loadbalancer-l2-vs-bgp.md).
- **Nó com GPU para IA local** em Talos direto no hardware: onde guardar os modelos, um app por vez, limite de potência escolhido em trabalho real, e benchmarks que mentem: [gpu-node-local-ai.md](../platform/gpu-node-local-ai.md).
- **Conheça a máquina antes de planejar:** canais de memória, slots PCIe, sensores: [know-your-hardware.md](../platform/know-your-hardware.md).
- **Por que o cluster "nunca parece estável":** disco que não termina nada, etcd em SSD ruim, e dois alertas: [disk-and-etcd-health.md](../platform/disk-and-etcd-health.md).
- **Agentes:** servidores MCP na rede de casa ([mcp-on-the-lan.md](../agents/mcp-on-the-lan.md)) e sessões longas com arquivo de objetivo e evidência ([long-sessions.md](../agents/long-sessions.md)).

## Camada 0 (rede)

Antes do Proxmox e do Kubernetes: plano de endereçamento que escala para várias casas, zonas com bloqueio padrão, uma rede só para DNS (forçar todo mundo a usar seus resolvers e ver quem fala com quem), nomes automáticos para cada dispositivo via DHCP, e poucas redes Wi-Fi com senha por tipo de dispositivo. Veja [docs/network/network-foundation.md](../network/network-foundation.md).
