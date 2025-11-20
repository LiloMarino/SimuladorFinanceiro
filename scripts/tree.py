import os
from collections import defaultdict
from pathlib import Path

import yaml


def load_descriptions(yaml_path: Path) -> dict[str, str]:
    """
    Carrega um arquivo YAML contendo descrições para arquivos e pastas.

    Cada chave no YAML representa o caminho relativo (arquivo ou pasta),
    e o valor é uma string com a descrição associada.

    Normaliza as chaves removendo barras finais '/' para padronizar a consulta.

    Exemplo de YAML:
        backend/: Lógica do backend em Flask
        backend/database.py: Configuração do banco de dados

    Args:
        yaml_path (Path): Caminho para o arquivo YAML de descrições.

    Returns:
        dict[str, str]: Dicionário com as chaves normalizadas (sem barra final)
                        e suas descrições correspondentes.
    """
    with open(yaml_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    normalized = {}
    for k, v in raw.items():
        key_norm = k.rstrip("/")
        normalized[key_norm] = v
    return normalized


def build_tree(paths: list[str]) -> dict:
    """
    Constrói uma estrutura de árvore (dicionários aninhados) a partir
    de uma lista de caminhos de arquivos e pastas.

    Essa estrutura permite fácil impressão em formato de árvore hierárquica.

    Args:
        paths (list[str]): Lista de caminhos relativos de arquivos/pastas.

    Returns:
        dict: Dicionário aninhado representando a hierarquia da árvore.
    """
    tree = lambda: defaultdict(tree)
    root = tree()
    for path in paths:
        parts = Path(path).parts
        current = root
        for part in parts:
            current = current[part]
    return root


def gather_lines(
    d: dict,
    prefix: str = "",
    base_path: str = "",
    descriptions: dict[str, str] | None = None,
) -> list[tuple[str, str]]:
    """
    Gera recursivamente uma lista de linhas formatadas para impressão da árvore,
    junto com comentários opcionais para cada item.

    Cada linha contém o prefixo visual da árvore (com '├──', '└──', etc.)
    e o nome do arquivo/pasta. Se houver descrição, ela é associada.

    Args:
        d (dict): Estrutura de árvore (dicionário aninhado) a ser percorrida.
        prefix (str): Prefixo a ser aplicado na linha atual (para indentação).
        base_path (str): Caminho base usado para construir o caminho completo
                         e consultar as descrições.
        descriptions (dict[str, str] | None): Dicionário com descrições para
                                             arquivos/pastas (opcional).

    Returns:
        list[tuple[str, str]]: Lista de tuplas contendo (linha_texto, comentário).
    """
    entries = sorted(d.items())
    lines = []

    for i, (key, subtree) in enumerate(entries):
        is_dir = bool(subtree)
        key_display = key + "/" if is_dir else key

        # Gera caminho completo relativo para buscar descrição
        path_joined = os.path.join(base_path, key) if base_path else key
        full_path_norm = path_joined.replace("\\", "/").rstrip("/")

        # Define os símbolos para conexão na árvore e extensão do prefixo
        connector = "└── " if i == len(entries) - 1 else "├── "
        extension = "    " if i == len(entries) - 1 else "│   "

        comment = ""
        if descriptions and full_path_norm in descriptions:
            comment = f"# {descriptions[full_path_norm]}"

        line_text = prefix + connector + key_display
        lines.append((line_text, comment))

        if subtree:
            lines.extend(
                gather_lines(subtree, prefix + extension, path_joined, descriptions)
            )

    return lines


def print_tree(d: dict, descriptions: dict[str, str] | None = None) -> None:
    """
    Imprime a árvore de arquivos/pastas com comentários alinhados.

    Realiza duas passadas: primeiro coleta todas as linhas com os comentários,
    depois calcula a largura máxima para alinhar os comentários verticalmente.

    Args:
        d (dict): Estrutura de árvore (dicionário aninhado) para imprimir.
        descriptions (dict[str, str] | None): Descrições opcionais para
                                             arquivos/pastas.
    """
    lines = gather_lines(d, descriptions=descriptions)

    # Calcula comprimento máximo da parte da árvore sem comentário
    max_len = max(len(line) for line, _ in lines)

    # Imprime linhas alinhando comentários na coluna max_len + 1
    for line_text, comment in lines:
        if comment:
            spaces = " " * (max_len - len(line_text) + 1)
            print(f"{line_text}{spaces}{comment}")
        else:
            print(line_text)


def save_descriptions_template(paths: list[str], output_path: Path):
    """
    Cria e salva um dicionário de todos os caminhos em um arquivo YAML,
    usando strings vazias como valores iniciais para preenchimento.
    """
    # 1. Cria um dicionário de caminhos com valores vazios ("")
    #    Normaliza as chaves, pois é assim que elas são lidas na função load_descriptions
    template_data = {path.replace("\\", "/").rstrip("/"): "" for path in paths}

    # 2. Ordena as chaves para melhor legibilidade
    sorted_data = dict(sorted(template_data.items()))

    # 3. Salva no arquivo YAML
    with open(output_path, "w", encoding="utf-8") as f:
        # Usa o Dumper padrão do YAML com sort_keys=False para manter a ordem
        yaml.dump(sorted_data, f, default_flow_style=False, sort_keys=False)

    print(f"✅ Esqueleto de descrições gerado em: {output_path}")
    print("Preencha as strings vazias com suas descrições.")


if __name__ == "__main__":
    # 1) Obtém a lista de arquivos versionados no Git (respeita .gitignore)
    with os.popen("git ls-files") as f:
        files = [line.strip() for line in f if line.strip()]

    desc_path = Path(__file__).parent / "tree_descriptions.yaml"
    if not desc_path.exists():
        save_descriptions_template(files, desc_path)
        print(
            "\nAgora, preencha as descrições em 'tree_descriptions.yaml' e execute novamente."
        )
        exit(0)

    # 2) Lê as descrições do arquivo YAML, se existir
    descriptions = load_descriptions(desc_path) if desc_path.exists() else {}

    # 3) Monta a árvore de diretórios/arquivos
    tree = build_tree(files)

    # 4) Captura o nome da pasta atual (nome do repositório)
    repo_name = os.path.basename(os.getcwd())
    print(f"{repo_name}/")

    # 5) Imprime a árvore com comentários alinhados
    print_tree(tree, descriptions=descriptions)
