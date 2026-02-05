import os
from collections import defaultdict
from pathlib import Path

import yaml

STOP_DIRS = {"docs", "components"}


def load_descriptions(yaml_path: Path) -> dict[str, str]:
    """
    Lê um arquivo YAML onde cada chave é um caminho relativo
    (arquivo ou pasta) e o valor é sua descrição.
    Normaliza removendo barras finais.
    """
    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
    return {k.rstrip("/"): v for k, v in raw.items()}


def normalize_path(path: str, stop_dirs: set[str]) -> str:
    """
    Trunca o path ao encontrar um diretório terminal.
    """
    parts = Path(path).parts
    normalized = []

    for part in parts:
        normalized.append(part)
        if part in stop_dirs:
            break

    return Path(*normalized).as_posix()


def extract_dirs_from_files(files: list[str], stop_dirs: set[str]) -> set[str]:
    dirs: set[str] = set()

    for file in files:
        path = Path(file)

        for parent in path.parents:
            if parent == Path():
                break

            normalized = normalize_path(parent.as_posix(), stop_dirs)
            dirs.add(normalized)

    return dirs


def build_tree(paths: list[str]) -> dict:
    def tree():
        return defaultdict(tree)

    root = tree()

    for path in sorted(set(paths)):
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

        connector = "└── " if is_last else "├── "
        extension = "    " if is_last else "│   "

        full_path = f"{base_path}/{key}" if base_path else key

        comment = (
            f"# {descriptions[full_path]}"
            if descriptions and full_path in descriptions
            else ""
        )

        lines.append((prefix + connector + f"{key}/", comment))

        lines.extend(gather_lines(subtree, prefix + extension, full_path, descriptions))

    return lines


def print_tree(d: dict, descriptions: dict[str, str] | None = None):
    """
    Imprime a árvore alinhando os comentários à direita.
    """
    lines = gather_lines(d, descriptions=descriptions)
    max_len = max(len(line) for line, _ in lines) if lines else 0

    for text, comment in lines:
        if comment:
            print(text + " " * (max_len - len(text) + 1) + comment)
        else:
            print(text)


def save_descriptions_template(dirs: list[str], output_path: Path):
    """
    Gera um YAML contendo todas as pastas e arquivos do repo
    com descrições vazias (template para preenchimento).
    """
    template = {f"{d}/": "" for d in sorted(dirs)}

    yaml.dump(
        template,
        output_path.open("w", encoding="utf-8"),
        default_flow_style=False,
        sort_keys=False,
    )

    print(f"✅ Template criado: {output_path}")
    print("Preencha as descrições e execute novamente.")


if __name__ == "__main__":
    with os.popen("git ls-files") as f:
        files = [line.strip() for line in f if line.strip()]

    dirs = list(extract_dirs_from_files(files, STOP_DIRS))
    tree = build_tree(dirs)

    desc_path = Path(__file__).parent / "tree_descriptions.yaml"

    if not desc_path.exists():
        save_descriptions_template(dirs, desc_path)
        exit(0)

    descriptions = load_descriptions(desc_path)

    print(f"{Path.cwd().name}/")
    print_tree(tree, descriptions)
