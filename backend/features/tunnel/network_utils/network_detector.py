import logging
import platform
import re
import socket
import subprocess
from collections.abc import Iterable

from backend.features.tunnel.network_utils.network_interface import NetworkInterface
from backend.features.tunnel.network_utils.network_types import NetworkType

logger = logging.getLogger(__name__)


class NetworkDetector:
    """
    Detector de interfaces de rede locais e VPNs.

    Responsável por:
    - Descobrir IPs locais usando hostname resolution e parsing de ifconfig/ipconfig
    - Identificar tipo de rede (Radmin, Hamachi, Tailscale, LAN) via ranges de IP
    - Executar comandos de sistema operacional para listar interfaces
    - Retornar lista de NetworkInterface com IP e tipo
    """

    def detect(self) -> list[NetworkInterface]:
        ips = self._get_local_ips()
        interfaces: list[NetworkInterface] = []

        for ip in ips:
            kind = self._detect_network_type(ip)
            if not kind:
                continue

            interfaces.append(
                NetworkInterface(
                    ip=ip,
                    kind=kind,
                )
            )

        return interfaces

    # =========================
    # IP discovery
    # =========================

    def _get_local_ips(self) -> Iterable[str]:
        ips: set[str] = set()

        # hostname resolution (best-effort)
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            if ip and not ip.startswith("127."):
                ips.add(ip)
        except OSError:
            pass

        system = platform.system()

        if system == "Windows":
            ips |= self._from_command(["ipconfig"], r"IPv4.*?(\d+\.\d+\.\d+\.\d+)")
        elif system == "Linux":
            ips |= self._from_command(["ip", "addr"], r"inet (\d+\.\d+\.\d+\.\d+)")
        elif system == "Darwin":
            ips |= self._from_command(["ifconfig"], r"inet (\d+\.\d+\.\d+\.\d+)")

        return ips

    def _from_command(self, command: list[str], pattern: str) -> set[str]:
        found: set[str] = set()

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=5,
            )

            for line in result.stdout.splitlines():
                match = re.search(pattern, line)
                if match:
                    ip = match.group(1)
                    if not ip.startswith("127."):
                        found.add(ip)

        except subprocess.TimeoutExpired:
            logger.warning(f"Comando {' '.join(command)} expirou (timeout)")
        except OSError as e:
            logger.debug(f"Erro ao executar {' '.join(command)}: {e}")

        return found

    # =========================
    # Network classification
    # =========================

    def _detect_network_type(self, ip: str) -> NetworkType | None:
        octets = ip.split(".")
        if len(octets) != 4:
            return None

        try:
            first = int(octets[0])
            second = int(octets[1])
        except ValueError:
            return None

        # VPNs conhecidas
        if first == 26:
            return NetworkType.RADMIN
        if first == 25:
            return NetworkType.HAMACHI
        if first == 100:
            return NetworkType.TAILSCALE

        # LAN privada
        if (
            (first == 192 and second == 168)
            or first == 10
            or (first == 172 and 16 <= second <= 31)
        ):
            return NetworkType.LAN

        return None
