from fastapi import APIRouter, status

from backend.core.dependencies import HostVerified
from backend.core.dto.tunnel_status import TunnelStatusDTO
from backend.core.runtime.tunnel_manager import TunnelManager

tunnel_router = APIRouter(prefix="/api/tunnel", tags=["Tunnel"])


@tunnel_router.post(
    "/start",
    response_model=TunnelStatusDTO,
    summary="Iniciar túnel",
    description="Inicia o túnel de rede para exposição da API (apenas o host pode executar).",
)
async def start_tunnel(_: HostVerified):
    """
    Inicia o túnel de rede.
    """
    status = await TunnelManager.start_tunnel()
    return status


@tunnel_router.post(
    "/stop",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Parar túnel",
    description="Encerra o túnel de rede (apenas o host pode executar).",
)
async def stop_tunnel(_: HostVerified):
    """
    Encerra o túnel de rede.
    """
    await TunnelManager.stop_tunnel()


@tunnel_router.get(
    "/status",
    response_model=TunnelStatusDTO,
    summary="Obter status do túnel",
    description="Retorna o status atual do túnel (ativo/inativo, URL, provider configurado).",
)
def get_tunnel_status():
    """
    Retorna o status atual do túnel.
    """
    status = TunnelManager.get_status()
    return status
