type Rgb = [number, number, number];
type Lab = [number, number, number];

function parseHex(hex: string): Rgb {
  const value = hex.replace("#", "");
  return [0, 2, 4].map((start) => parseInt(value.slice(start, start + 2), 16)) as Rgb;
}

/** Canal sRGB (0-255) para luz linear (0-1). */
function linear(channel: number): number {
  const c = channel / 255;
  return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
}

/** Hex para luz linear nos três canais. */
function linearRgb(hex: string): Rgb {
  const [r, g, b] = parseHex(hex);
  return [linear(r), linear(g), linear(b)];
}

function luminance(hex: string): number {
  const [r, g, b] = linearRgb(hex);
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

/** Razão de contraste WCAG entre duas cores hex: de 1 (iguais) a 21 (preto no branco). */
export function contrastRatio(a: string, b: string): number {
  const [first, second] = [luminance(a), luminance(b)];
  return (Math.max(first, second) + 0.05) / (Math.min(first, second) + 0.05);
}

/** Hex para CIELAB com branco de referência D65. */
function toLab(hex: string): Lab {
  const [r, g, b] = linearRgb(hex);
  const x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047;
  const y = 0.2126729 * r + 0.7151522 * g + 0.072175 * b;
  const z = (0.0193339 * r + 0.119192 * g + 0.9503041 * b) / 1.08883;
  const f = (t: number) => (t > 216 / 24389 ? Math.cbrt(t) : ((24389 / 27) * t + 16) / 116);
  const [fx, fy, fz] = [f(x), f(y), f(z)];
  return [116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)];
}

const toRad = (deg: number) => (deg * Math.PI) / 180;
const toDeg = (rad: number) => (rad * 180) / Math.PI;

/** Ângulo de matiz em graus, de 0 a 360. */
function hueAngle(b: number, aPrime: number): number {
  if (b === 0 && aPrime === 0) return 0;
  const h = toDeg(Math.atan2(b, aPrime));
  return h >= 0 ? h : h + 360;
}

/** CIEDE2000 entre dois valores CIELAB (Sharma, Wu e Dalal, 2005). */
export function deltaE2000Lab(first: Lab, second: Lab): number {
  const [l1, a1, b1] = first;
  const [l2, a2, b2] = second;

  const c1 = Math.hypot(a1, b1);
  const c2 = Math.hypot(a2, b2);
  const cMean = (c1 + c2) / 2;
  const g = 0.5 * (1 - Math.sqrt(cMean ** 7 / (cMean ** 7 + 25 ** 7)));
  const a1p = (1 + g) * a1;
  const a2p = (1 + g) * a2;
  const c1p = Math.hypot(a1p, b1);
  const c2p = Math.hypot(a2p, b2);
  const h1p = hueAngle(b1, a1p);
  const h2p = hueAngle(b2, a2p);

  const dLp = l2 - l1;
  const dCp = c2p - c1p;
  let dhp = 0;
  if (c1p * c2p !== 0) {
    dhp = h2p - h1p;
    if (dhp > 180) dhp -= 360;
    else if (dhp < -180) dhp += 360;
  }
  const dHp = 2 * Math.sqrt(c1p * c2p) * Math.sin(toRad(dhp / 2));

  const lMean = (l1 + l2) / 2;
  const cpMean = (c1p + c2p) / 2;
  let hpMean = h1p + h2p;
  if (c1p * c2p !== 0) {
    if (Math.abs(h1p - h2p) <= 180) hpMean /= 2;
    else hpMean = (hpMean + (h1p + h2p < 360 ? 360 : -360)) / 2;
  }

  const t =
    1 -
    0.17 * Math.cos(toRad(hpMean - 30)) +
    0.24 * Math.cos(toRad(2 * hpMean)) +
    0.32 * Math.cos(toRad(3 * hpMean + 6)) -
    0.2 * Math.cos(toRad(4 * hpMean - 63));
  const dTheta = 30 * Math.exp(-(((hpMean - 275) / 25) ** 2));
  const rc = 2 * Math.sqrt(cpMean ** 7 / (cpMean ** 7 + 25 ** 7));
  const sl = 1 + (0.015 * (lMean - 50) ** 2) / Math.sqrt(20 + (lMean - 50) ** 2);
  const sc = 1 + 0.045 * cpMean;
  const sh = 1 + 0.015 * cpMean * t;
  const rt = -Math.sin(toRad(2 * dTheta)) * rc;

  return Math.sqrt((dLp / sl) ** 2 + (dCp / sc) ** 2 + (dHp / sh) ** 2 + rt * (dCp / sc) * (dHp / sh));
}

/** Distância ΔE (CIEDE2000) entre duas cores hex: abaixo de 2 ninguém nota, acima de 20 são outras cores. */
export function deltaE2000(a: string, b: string): number {
  return deltaE2000Lab(toLab(a), toLab(b));
}
