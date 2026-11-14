import { isValidElement, type ReactElement } from "react";

type AnyProps = Record<string, unknown>;

/** Os elementos da árvore devolvida por um componente (filhos e props como `render`) que satisfazem `match`. */
export function findElements(
  node: unknown,
  match: (element: ReactElement<AnyProps>) => boolean,
): ReactElement<AnyProps>[] {
  if (Array.isArray(node)) return node.flatMap((child) => findElements(child, match));
  if (!isValidElement<AnyProps>(node)) return [];
  const self = match(node) ? [node] : [];
  return [...self, ...Object.values(node.props).flatMap((value) => findElements(value, match))];
}

/** Dispara o `onClick` do elemento, como o clique do jogador. */
export function click(element: ReactElement<AnyProps> | undefined) {
  const onClick = element?.props["onClick"];
  if (typeof onClick !== "function") throw new Error("O elemento não tem onClick");
  (onClick as () => void)();
}
