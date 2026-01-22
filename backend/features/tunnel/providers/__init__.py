from backend.features.tunnel.providers.lan_provider import LANProvider
from backend.features.tunnel.providers.placeholder_provider import PlaceholderProvider

# Providers disponíveis para túneis de rede
# - "lan": Conexão direta via LAN/VPN (Radmin, Hamachi, Tailscale)
# - "localtunnel": Túnel público automático (em desenvolvimento)
# - "playit": Túnel para jogos (em desenvolvimento)
# - "zrok": Túnel open-source (em desenvolvimento)
AVAILABLE_PROVIDERS = {
    "lan": LANProvider,
    "placeholder": PlaceholderProvider,
}
