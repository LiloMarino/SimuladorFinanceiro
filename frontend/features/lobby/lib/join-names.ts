/** "Ana", "Ana e Caio", "Ana, Caio e Duda" */
export function joinNames(names: string[]) {
  if (names.length <= 1) return names.join("");
  return `${names.slice(0, -1).join(", ")} e ${names[names.length - 1]}`;
}
