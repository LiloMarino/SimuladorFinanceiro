/** A parte da contribuição que vai ao Congresso, em reais; sem chapa na presidência, tudo vai a ele. */
export function congressAmount(monthly: number, share: number, runs: boolean) {
  return (runs ? (monthly * share) / 100 : monthly).toFixed(2);
}

/** A fatia do Congresso (0 a 100) que uma contribuição já salva representa. */
export function congressShare(contribution: string, congress: string) {
  const total = Number(contribution);
  return total > 0 ? Math.round((Number(congress) / total) * 100) : 0;
}
