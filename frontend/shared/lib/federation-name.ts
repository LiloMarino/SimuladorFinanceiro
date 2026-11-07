/** O nome que a federação ganha quando o fundador não escolhe outro. */
export function defaultFederationName(own: string, partner: string) {
  return `Federação ${own}–${partner}`;
}
