/**
 * Converte um objeto em FormData.
 * File/Blob são preservados, o resto é convertido para string.
 */
export function toFormData(obj: Record<string, string | number | boolean | File | Blob | null | undefined>): FormData {
  const formData = new FormData();
  for (const [key, value] of Object.entries(obj)) {
    if (value === undefined || value === null) continue;
    formData.append(key, value instanceof Blob ? value : String(value));
  }
  return formData;
}
