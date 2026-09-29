# Português (resumo)

Caminho **homelab + agentes de IA → engenharia de plataforma**.

1. Leia [../00-philosophy.md](../00-philosophy.md) (inglês técnico).
2. Siga [../setup/](../setup/) na ordem (01 → 13).
3. Skills no Hermes: `bash scripts/install-skills.sh --hermes`
4. Issues + board como fila de trabalho.
5. Footguns: [../lessons/hard-won.md](../lessons/hard-won.md)
6. Índice: [../MAP.md](../MAP.md)

**Ideia:** Kubernetes é a estrada. GitOps, CNI, tunnel e o agente andam nela. A IA multiplica com skills e permissões certas — não com cluster-admin solto.


## Novo: camada 0 (rede)

Antes do Proxmox e do Kubernetes: plano de endereçamento que escala para várias casas, zonas com bloqueio padrão, uma rede só para DNS (forçar todo mundo a usar seus resolvers e ver quem fala com quem), nomes automáticos para cada dispositivo via DHCP, e poucas redes Wi-Fi com senha por tipo de dispositivo. Veja [docs/network/network-foundation.md](../network/network-foundation.md).
