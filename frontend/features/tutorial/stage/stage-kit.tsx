import { useEffect, useEffectEvent, useState } from "react";
import { motion, useReducedMotion } from "motion/react";
import { CircleCheck } from "lucide-react";
import { cn } from "@/shared/lib/utils";
import { useStage } from "./stage-context";
import type { Finder } from "./targets";

export interface Rect {
  x: number;
  y: number;
  width: number;
  height: number;
}

const RETRY_MS = 300;
const RETRIES = 4;
const SETTLE_AGAIN_MS = 700;

/**
 * Mede o elemento que o `finder` acha, em px de projeto do palco. O alvo pode ainda estar
 * entrando em cena: a leitura espera `settle` ms e tenta de novo antes de dar a cena por quebrada,
 * o que o ErrorBoundary da ilustração mostra como aviso.
 */
function useTargetRect(finder: Finder | null, id: string, settle = 450) {
  const { root, scale } = useStage();
  const [rect, setRect] = useState<Rect | null>(null);
  const [failure, setFailure] = useState<Error | null>(null);
  const active = finder !== null;

  const read = useEffectEvent((): Rect | null => {
    const base = root.current;
    const element = base && finder?.(base);
    if (!base || !element) return null;
    const box = element.getBoundingClientRect();
    const origin = base.getBoundingClientRect();
    return {
      x: (box.left - origin.left) / scale,
      y: (box.top - origin.top) / scale,
      width: box.width / scale,
      height: box.height / scale,
    };
  });

  useEffect(() => {
    if (!active) return;
    const timers: ReturnType<typeof setTimeout>[] = [];
    const attempt = (n: number) => {
      const found = read();
      if (found) {
        setRect(found);
        // Segunda leitura: o alvo pode ter terminado de assentar depois da primeira
        timers.push(setTimeout(() => setRect(read() ?? found), SETTLE_AGAIN_MS));
      } else if (n < RETRIES) timers.push(setTimeout(() => attempt(n + 1), RETRY_MS));
      else setFailure(new Error(`A animação não achou o alvo "${id}"`));
    };
    timers.push(setTimeout(() => attempt(0), settle));
    return () => timers.forEach(clearTimeout);
  }, [id, scale, active, settle]);

  if (failure) throw failure;
  return rect;
}

interface CursorProps {
  finder: Finder | null;
  /** Identifica o alvo: o cursor volta a medir quando ele muda. */
  id: string;
  /** Ponto do alvo em que o cursor para, como fração da largura e da altura. */
  at?: readonly [number, number];
  /** Pulso de clique ao chegar. */
  click?: boolean;
  /** De onde o cursor parte antes do primeiro alvo. */
  start: { x: number; y: number };
  /** Espera até o alvo terminar de entrar em cena, em ms. */
  settle?: number;
}

/** Cursor do exemplo: desliza até o alvo medido no DOM real do palco. */
export function Cursor({ finder, id, at = [0.5, 0.5], click = false, start, settle }: CursorProps) {
  const rect = useTargetRect(finder, id, settle);
  const reduced = useReducedMotion();
  const x = rect ? rect.x + rect.width * at[0] : start.x;
  const y = rect ? rect.y + rect.height * at[1] : start.y;

  return (
    <motion.div
      className="pointer-events-none absolute top-0 left-0 z-30"
      animate={{ x, y }}
      transition={{ duration: reduced ? 0 : 0.7, ease: "easeInOut" }}
    >
      {click && rect && !reduced && (
        <motion.span
          key={id}
          className="absolute -top-3 -left-3 size-6 rounded-full bg-primary/40"
          initial={{ scale: 0.4, opacity: 0.9 }}
          animate={{ scale: 1.8, opacity: 0 }}
          transition={{ delay: 0.75, duration: 0.5 }}
        />
      )}
      <svg width="22" height="22" viewBox="0 0 24 24" className="drop-shadow-[0_2px_3px_rgba(0,0,0,0.3)]">
        <path d="M5 3l14 7-6 2-2 6z" fill="var(--foreground)" stroke="var(--color-card)" strokeWidth="1.5" strokeLinejoin="round" />
      </svg>
    </motion.div>
  );
}

interface HighlightProps {
  finder: Finder | null;
  id: string;
  className?: string;
  settle?: number;
}

/** Contorno azul no alvo: faz o papel do foco e do mouse em cima, que o palco sem interação não tem. */
export function Highlight({ finder, id, className, settle }: HighlightProps) {
  const rect = useTargetRect(finder, id, settle);
  if (!finder || !rect) return null;
  return (
    <motion.div
      key={id}
      className={cn("pointer-events-none absolute z-20 rounded-lg ring-3 ring-primary/30", className)}
      style={{ left: rect.x, top: rect.y, width: rect.width, height: rect.height }}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    />
  );
}

interface StepMarkerProps {
  finder: Finder | null;
  id: string;
  /** Número do passo do texto, a partir de 1. */
  step: number;
  settle?: number;
}

/** Marcador numerado à esquerda do alvo: diz a que passo do texto a cena corresponde. */
export function StepMarker({ finder, id, step, settle }: StepMarkerProps) {
  const rect = useTargetRect(finder, id, settle);
  if (!finder || !rect) return null;
  return (
    <motion.div
      className="pointer-events-none absolute z-20 flex items-center"
      initial={false}
      animate={{ left: Math.max(4, rect.x - 46), top: rect.y + rect.height / 2 - 12 }}
      transition={{ duration: 0.5, ease: "easeInOut" }}
    >
      <b className="inline-flex size-6 items-center justify-center rounded-full bg-primary text-xs text-primary-foreground ring-3 ring-card">
        {step}
      </b>
      <span className="h-0.5 w-[22px] bg-primary" />
    </motion.div>
  );
}

/** Tenta a ação até o alvo existir: ele pode ainda estar entrando em cena. */
function useWhenFound(finder: Finder, id: string, action: (element: HTMLElement) => void, delay: number) {
  const { root } = useStage();
  const run = useEffectEvent(action);
  const find = useEffectEvent(() => (root.current ? finder(root.current) : null));

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;
    const attempt = (n: number) => {
      const element = find();
      if (element) run(element);
      else if (n < RETRIES) timer = setTimeout(() => attempt(n + 1), RETRY_MS);
    };
    timer = setTimeout(() => attempt(0), delay);
    return () => clearTimeout(timer);
  }, [id, delay]);
}

/** Escreve no campo pelo mesmo caminho do teclado: o React recebe um evento de input e a boleta reage. */
function setInputValue(input: HTMLInputElement, value: string) {
  const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
  setter?.call(input, value);
  input.dispatchEvent(new Event("input", { bubbles: true }));
}

interface TypeIntoProps {
  finder: Finder;
  /** O texto que o campo mostra nesta cena. */
  text: string;
  /** Digita caractere a caractere em vez de escrever de uma vez. */
  typing: boolean;
  /** Espera antes de começar, para o cursor chegar ao campo. */
  delay?: number;
  /** Tempo entre um caractere e o seguinte, em ms. */
  interval?: number;
}

export function TypeInto({ finder, text, typing, delay = 0, interval = 350 }: TypeIntoProps) {
  const { root } = useStage();
  const reduced = useReducedMotion();
  const write = useEffectEvent((value: string) => {
    const element = root.current && finder(root.current);
    if (element instanceof HTMLInputElement && element.value !== value) setInputValue(element, value);
  });

  // Digitação: um caractere a cada `interval`; sem digitar, o campo recebe o texto inteiro assim que existe
  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = [];
    if (typing && !reduced) {
      for (let length = 1; length <= text.length; length++) {
        timers.push(setTimeout(() => write(text.slice(0, length)), delay + length * interval));
      }
    } else {
      for (let n = 0; n <= RETRIES; n++) timers.push(setTimeout(() => write(text), n * RETRY_MS));
    }
    return () => timers.forEach(clearTimeout);
  }, [text, typing, reduced, delay, interval]);

  return null;
}

interface PressWhenProps {
  finder: Finder;
  id: string;
  /** O botão de alternância deve estar apertado nesta cena. */
  pressed: boolean;
  delay?: number;
}

/** Deixa o seletor no estado da cena: clica só se ele ainda não está assim. */
export function PressWhen({ finder, id, pressed, delay = 0 }: PressWhenProps) {
  useWhenFound(
    finder,
    `${id}:${pressed}`,
    (element) => {
      if ((element.getAttribute("aria-pressed") === "true") !== pressed) element.click();
    },
    delay,
  );
  return null;
}

/** Aviso de compra feita, desenhado dentro do palco e fora do Toaster real. */
export function StageToast({ children }: { children: string }) {
  return (
    <motion.div
      className="absolute right-4 bottom-4 z-30 flex max-w-[260px] items-center gap-2.5 rounded-[10px] bg-toast px-3.5 py-3 text-[13px] text-toast-foreground shadow-lg"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
    >
      <CircleCheck className="size-4 shrink-0 text-toast-success" />
      {children}
    </motion.div>
  );
}
