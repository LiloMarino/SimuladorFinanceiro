"""
Simulador Financeiro - Código-fonte principal

Copyright (C) 2025 Murilo Marino

Este programa é software livre: você pode redistribuí-lo e/ou modificá-lo
sob os termos da Licença Pública Geral GNU publicada pela Free Software Foundation,
na versão 3 da licença, ou (a seu critério) qualquer versão posterior.

Este programa é distribuído na esperança de que seja útil,
mas SEM NENHUMA GARANTIA; sem mesmo a garantia implícita de
COMERCIALIZAÇÃO ou ADEQUAÇÃO A UM DETERMINADO PROPÓSITO.
Consulte a Licença Pública Geral GNU para mais detalhes.

Você deve ter recebido uma cópia da Licença Pública Geral GNU
junto com este programa. Caso não, veja <https://www.gnu.org/licenses/>.
"""

from backend.data_loader import atualizar_ativo

if __name__ == "__main__":
    atualizar_ativo("PETR4.SA")
