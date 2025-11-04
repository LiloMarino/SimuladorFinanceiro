export const formatPrice = (value: number) => {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    minimumFractionDigits: 2,
  }).format(value);
};

export const formatCash = (cash?: number) => {
  if (cash === undefined) return "--";
  return cash.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
};
