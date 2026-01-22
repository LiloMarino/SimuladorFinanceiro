import platform
import re
import socket
import subprocess

from backend.core.logger import setup_logger
from backend.features.tunnel.tunnel_provider import TunnelProvider

logger = setup_logger(__name__)


class LANProvider(TunnelProvider):
    """
    Provider para conexões LAN diretas via VPN ou rede local.

    Detecta automaticamente:
    - Radmin VPN (26.x.x.x)
    - LogMeIn Hamachi (25.x.x.x)
    - Tailscale (100.x.x.x)
    - IP local (192.168.x.x, 10.x.x.x, 172.16-31.x.x)

    Ideal para usuários avançados que usam Radmin/Hamachi/VPN própria.
    Não inicia nenhum processo - apenas detecta IPs disponíveis.

    Prioridade: Radmin > Hamachi > Tailscale > LAN Local
    """

    def __init__(self):
        self._active = False
        self._detected_ips: list[dict] = []
        self._port: int | None = None
        self._initialized = False

    @property
    def name(self) -> str:
        return "lan"

    def _get_local_ips(self) -> list[str]:
        """Detecta todos os IPs locais da máquina."""
        ips = []

        try:
            # IP primário via socket
            hostname = socket.gethostname()
            primary_ip = socket.gethostbyname(hostname)
            if primary_ip and primary_ip != "127.0.0.1":
                ips.append(primary_ip)
        except Exception as e:
            logger.debug(f"Não foi possível obter IP primário: {e}")

        # IPs de todas as interfaces
        if platform.system() == "Windows":
            try:
                result = subprocess.run(
                    ["ipconfig"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                for line in result.stdout.split("\n"):
                    # Procura por "Endereço IPv4" ou "IPv4 Address"
                    if "IPv4" in line:
                        # Extrai o IP usando regex
                        match = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line)
                        if match:
                            ip = match.group(1)
                            if ip and ip != "127.0.0.1" and ip not in ips:
                                ips.append(ip)
            except subprocess.TimeoutExpired:
                logger.warning("ipconfig expirou (timeout)")
            except Exception as e:
                logger.debug(f"Erro ao executar ipconfig: {e}")

        elif platform.system() == "Linux":
            try:
                result = subprocess.run(
                    ["ip", "addr"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                for line in result.stdout.split("\n"):
                    if "inet " in line and not line.strip().startswith("127"):
                        match = re.search(
                            r"inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",
                            line,
                        )
                        if match:
                            ip = match.group(1)
                            if ip not in ips:
                                ips.append(ip)
            except Exception as e:
                logger.debug(f"Erro ao executar ip addr: {e}")

        elif platform.system() == "Darwin":  # macOS
            try:
                result = subprocess.run(
                    ["ifconfig"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                for line in result.stdout.split("\n"):
                    if "inet " in line and not line.strip().startswith("127"):
                        match = re.search(
                            r"inet (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})",
                            line,
                        )
                        if match:
                            ip = match.group(1)
                            if ip not in ips:
                                ips.append(ip)
            except Exception as e:
                logger.debug(f"Erro ao executar ifconfig: {e}")

        return ips

    def _detect_network_type(self, ip: str) -> str:
        """Identifica o tipo de rede baseado no IP."""
        octets = ip.split(".")

        if len(octets) != 4:
            return "unknown"

        try:
            first = int(octets[0])
            second = int(octets[1])

            # VPNs conhecidas (prioridade)
            if first == 26:
                return "radmin"
            elif first == 25:
                return "hamachi"
            elif first == 100:
                return "tailscale"

            # LANs privadas
            elif (
                (first == 192 and second == 168)
                or first == 10
                or (first == 172 and 16 <= second <= 31)
            ):
                return "lan"

        except ValueError:
            pass

        return "unknown"

    def _get_network_name(self, network_type: str) -> str:
        """Retorna nome amigável para o tipo de rede."""
        names = {
            "radmin": "Radmin VPN",
            "hamachi": "LogMeIn Hamachi",
            "tailscale": "Tailscale",
            "lan": "LAN Local",
            "unknown": "Rede Desconhecida",
        }
        return names.get(network_type, "Desconhecido")

    async def start(self, port: int) -> str:
        """
        Detecta e coleta IPs disponíveis.
        Não inicia nenhum processo - apenas coleta informações.
        """
        self._port = port
        self._initialize_ips()
        self._initialized = True
        return self._get_best_url() or ""

    def _initialize_ips(self) -> None:
        """Detecta e classifica IPs disponíveis (método sincronizado)."""
        self._detected_ips = []

        ips = self._get_local_ips()

        if not ips:
            logger.warning(
                "⚠️ Nenhuma interface de rede detectada. "
                "Verifique sua conexão ou se Radmin/Hamachi está ativo."
            )
            self._active = False
            return

        # Processa e classifica cada IP
        for ip in ips:
            network_type = self._detect_network_type(ip)

            if network_type == "unknown":
                continue  # Ignora IPs desconhecidos

            url = f"http://{ip}:{self._port}"

            self._detected_ips.append(
                {
                    "ip": ip,
                    "url": url,
                    "type": network_type,
                    "name": self._get_network_name(network_type),
                }
            )

        if not self._detected_ips:
            logger.warning(
                "⚠️ Nenhuma rede válida detectada (VPN/LAN). "
                "Ative Radmin VPN/Hamachi ou conecte à rede local."
            )
            self._active = False
            return

        self._active = True

        # Log das detecções com ícones
        logger.info(f"🌐 IPs LAN detectados (Porta {self._port}):")
        for detected in self._detected_ips:
            icon = self._get_icon(detected["type"])
            logger.info(f"  {icon} [{detected['name']}] {detected['url']}")

        # Aviso sobre firewall
        logger.warning(
            f"⚠️ Para aceitar conexões externas, abra a porta {self._port} no firewall:"
        )
        logger.warning("   Windows: Settings > Privacy & Security > Firewall")
        logger.warning("   Linux: sudo ufw allow {self._port}/tcp")
        logger.warning("   macOS: System Preferences > Security & Privacy")

    def _get_icon(self, network_type: str) -> str:
        """Retorna ícone para cada tipo de rede."""
        icons = {
            "radmin": "📡",
            "hamachi": "🔗",
            "tailscale": "🛰️",
            "lan": "🏠",
        }
        return icons.get(network_type, "🌐")

    def _get_best_url(self) -> str:
        """Retorna o melhor IP segundo prioridade: Radmin > Hamachi > Tailscale > LAN."""
        priority_order = ["radmin", "hamachi", "tailscale", "lan"]

        for network_type in priority_order:
            for detected in self._detected_ips:
                if detected["type"] == network_type:
                    return detected["url"]

        # Fallback (não deveria chegar aqui)
        return self._detected_ips[0]["url"] if self._detected_ips else ""

    async def stop(self) -> None:
        """Para o provider LAN (apenas limpa estado)."""
        self._active = False
        self._detected_ips = []
        self._port = None
        logger.info("🔌 Provider LAN desativado")

    def get_public_url(self) -> str | None:
        """Retorna o melhor IP detectado ou None."""
        if not self._active or not self._detected_ips:
            return None

        return self._get_best_url()

    def is_active(self) -> bool:
        """Verifica se há IPs detectados."""
        return self._active and len(self._detected_ips) > 0

    def get_all_urls(self) -> list[dict]:
        """Retorna TODOS os IPs detectados com metadados (para UI)."""
        return self._detected_ips if self._active else []
