// O modo debug vem do servidor depois do boot do front: até lá, debug e log ficam mudos.
let debugEnabled = false;

export function setDebugLogging(enabled: boolean) {
  debugEnabled = enabled;
}

export const logger = {
  debug: (...args: unknown[]) => {
    if (debugEnabled) console.debug(...args);
  },
  log: (...args: unknown[]) => {
    if (debugEnabled) console.log(...args);
  },
  warn: console.warn.bind(console),
  error: console.error.bind(console),
};
