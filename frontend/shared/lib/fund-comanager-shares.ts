// Co-gestores por gestora, contando os convites pendentes
export const MAX_COMANAGERS = 3;

/** O teto da parte de um co-gestor, em pontos percentuais: sobra ao menos 1 ponto para o gestor principal. */
export const maxSharePoints = (others: number) => Math.max(0, Math.round(100 - others) - 1);
