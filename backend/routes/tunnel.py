"""Network tunnel endpoints."""

from fastapi import APIRouter

from backend.core.dependencies import HostVerified
from backend.features.tunnel.tunnel_manager import TunnelManager

tunnel_router = APIRouter(prefix="/api/tunnel", tags=["Tunnel"])


@tunnel_router.post("/start")
async def start_tunnel(_: HostVerified):
    """
    Inicia o túnel de rede (apenas host).
    Returns:
        {
            "url": str,      # URL pública do túnel
            "provider": str  # Nome do provider usado
        }
    """
    result = await TunnelManager.start_tunnel()
    return result


@tunnel_router.post("/stop")
async def stop_tunnel(_: HostVerified):
    """
    Para o túnel ativo (apenas host).
    """
    await TunnelManager.stop_tunnel()
    return {"message": "Túnel parado com sucesso"}


@tunnel_router.get("/status")
def get_tunnel_status():
    """
    Retorna status do túnel (qualquer usuário).

    Returns:
        {
            "active": bool,          # Se túnel está ativo
            "url": str | None,       # URL pública se ativo
            "provider": str | None,  # Provider se ativo
            "enabled": bool          # Se túnel está habilitado na config
        }
    """
    return TunnelManager.get_status()
