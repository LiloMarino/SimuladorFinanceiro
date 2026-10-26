from backend.features.tunnel.providers.example_provider import ExampleProvider
from backend.features.tunnel.providers.lan_provider import LANProvider
from backend.features.tunnel.tunnel_provider import TunnelProvider

# Providers disponíveis para túneis de rede
# - "lan": Conexão direta via LAN/VPN (Radmin, Hamachi, Tailscale)
# - "localtunnel": Túnel público automático (em desenvolvimento)
# - "playit": Túnel para jogos (em desenvolvimento)
# - "zrok": Túnel open-source (em desenvolvimento)
AVAILABLE_PROVIDERS: dict[str, type[TunnelProvider]] = {
    "lan": LANProvider,
    "example": ExampleProvider,
}
