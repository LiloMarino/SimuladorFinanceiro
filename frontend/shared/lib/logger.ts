const isDev = import.meta.env.DEV;

export const logger = {
  debug: isDev ? console.debug.bind(console) : () => { },
  log: isDev ? console.log.bind(console) : () => { },
  warn: console.warn.bind(console),
  error: console.error.bind(console),
};
