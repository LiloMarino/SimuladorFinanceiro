import os
from collections import defaultdict
from pathlib import Path

import yaml


def load_descriptions(yaml_path: Path) -> dict[str, str]:
    """
    Lê um arquivo YAML onde cada chave é um caminho relativo
    (arquivo ou pasta) e o valor é sua descrição.
    Normaliza removendo barras finais.
    """
    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    return {k.rstrip("/"): v for k, v in raw.items()}


def build_tree(paths: list[str]) -> dict:
    """
    Constrói uma árvore (dicionários aninhados) a partir de uma lista de caminhos.
    """

    def tree():
        return defaultdict(tree)

    root = tree()

    for path in paths:
        current = root
        for part in Path(path).parts:
            current = current[part]

    return root


def gather_lines(
    d: dict,
    prefix: str = "",
    base_path: str = "",
    descriptions: dict[str, str] | None = None,
) -> list[tuple[str, str]]:
    """
    Percorre a árvore e gera linhas formatadas, retornando:
    (texto da árvore, comentário da descrição)
    """
    entries = sorted(d.items())
    lines = []

    for i, (key, subtree) in enumerate(entries):
        is_last = i == len(entries) - 1
        is_dir = bool(subtree)

        display = key + "/" if is_dir else key
        connector = "└── " if is_last else "├── "
        extension = "    " if is_last else "│   "

        full_path = Path(base_path) / key if base_path else key
        full_path = full_path.replace("\\", "/").rstrip("/")

        comment = (
            f"# {descriptions[full_path]}"
            if descriptions and full_path in descriptions
            else ""
        )

        line_text = prefix + connector + display
        lines.append((line_text, comment))

        if is_dir:
            lines.extend(
                gather_lines(subtree, prefix + extension, full_path, descriptions)
            )

    return lines


def print_tree(d: dict, descriptions: dict[str, str] | None = None):
    """
    Imprime a árvore alinhando os comentários à direita.
    """
    lines = gather_lines(d, descriptions=descriptions)
    max_len = max(len(line) for line, _ in lines)

    for text, comment in lines:
        if comment:
            print(text + " " * (max_len - len(text) + 1) + comment)
        else:
            print(text)


def save_descriptions_template(paths: list[str], output_path: Path):
    """
    Gera um YAML contendo todas as pastas e arquivos do repo
    com descrições vazias (template para preenchimento).
    """
    tree = build_tree(paths)
    template = {p.replace("\\", "/").rstrip("/"): "" for p in paths}

    def collect_dirs(subtree: dict, base=""):
        for key, child in subtree.items():
            current = f"{base}/{key}" if base else key
            normalized = current.replace("\\", "/").rstrip("/")

            if child:
                template[f"{normalized}/"] = ""
                collect_dirs(child, current)

    collect_dirs(tree)

    # Ordenação hierárquica simples
    def sort_key(item):
        path, _ = item
        parts = path.split("/")
        is_file = not path.endswith("/")
        return (*parts, is_file)

    sorted_template = dict(sorted(template.items(), key=sort_key))

    yaml.dump(
        sorted_template,
        output_path.open("w", encoding="utf-8"),
        default_flow_style=False,
        sort_keys=False,
    )

    print(f"✅ Template criado: {output_path}")
    print("Preencha as descrições e execute novamente.")


if __name__ == "__main__":
    with os.popen("git ls-files") as f:
        files = [line.strip() for line in f if line.strip()]

    desc_path = Path(__file__).parent / "tree_descriptions.yaml"

    if not desc_path.exists():
        save_descriptions_template(files, desc_path)
        exit(0)

    descriptions = load_descriptions(desc_path)
    tree = build_tree(files)

    print(f"{Path.cwd().name}/")
    print_tree(tree, descriptions)
