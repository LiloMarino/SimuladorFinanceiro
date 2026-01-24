from fastapi import APIRouter, status

from backend.core.dependencies import HostVerified
from backend.core.dto.tunnel_status import TunnelStatusDTO
from backend.core.runtime.tunnel_manager import TunnelManager

tunnel_router = APIRouter(prefix="/api/tunnel", tags=["Tunnel"])


@tunnel_router.post("/start", response_model=TunnelStatusDTO)
async def start_tunnel(_: HostVerified):
    """
    Inicia o túnel de rede (apenas host).
    """
    status = await TunnelManager.start_tunnel()
    return status


@tunnel_router.post("/stop", status_code=status.HTTP_204_NO_CONTENT)
async def stop_tunnel(_: HostVerified):
    """
    Para o túnel de rede (apenas host).
    """
    await TunnelManager.stop_tunnel()


@tunnel_router.get("/status", response_model=TunnelStatusDTO)
def get_tunnel_status():
    """
    Retorna status do túnel (qualquer usuário).

    Returns:
        JSON com status atual, URL (se ativo) e provider configurado.
    """
    status = TunnelManager.get_status()
    return status
