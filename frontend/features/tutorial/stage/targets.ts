/** Procura um elemento do palco; o cursor e o destaque apontam para o que ele devolve. */
export type Finder = (root: HTMLElement) => HTMLElement | null;

const normalize = (text: string | null) => (text ?? "").replace(/ /g, " ").replace(/\s+/g, " ").trim();

const all = (root: HTMLElement, selector: string) => Array.from(root.querySelectorAll<HTMLElement>(selector));

/** Linha da tabela que contém o texto (o ticker, por exemplo). */
export const tableRow =
  (text: string): Finder =>
  (root) =>
    all(root, "tr").find((row) => normalize(row.textContent).includes(text)) ?? null;

export const tableHeader =
  (text: string): Finder =>
  (root) =>
    all(root, "th").find((cell) => normalize(cell.textContent).includes(text)) ?? null;

export const byId =
  (id: string): Finder =>
  (root) =>
    root.querySelector<HTMLElement>(`#${id}`);

/** Botão cujo texto é exatamente este (o seletor "Limitada", o "Comprar" do par Comprar/Vender). */
export const buttonNamed =
  (text: string): Finder =>
  (root) =>
    all(root, "button").find((button) => normalize(button.textContent) === text) ?? null;

/** O último botão que começa com o texto: o de enviar a ordem vem depois dos seletores. */
export const lastButtonStartingWith =
  (text: string): Finder =>
  (root) =>
    all(root, "button")
      .filter((button) => normalize(button.textContent).startsWith(text))
      .at(-1) ?? null;

/** Primeiro elemento do seletor cujo texto é exatamente este. */
export const withText =
  (selector: string, text: string): Finder =>
  (root) =>
    all(root, selector).find((element) => normalize(element.textContent) === text) ?? null;

export const bySelector =
  (selector: string): Finder =>
  (root) =>
    root.querySelector<HTMLElement>(selector);
