import { useEffect, useRef, useState } from "react";
import type { KeyboardEvent } from "react";
import { Badge } from "@/shared/components/ui/badge";
import { Input } from "@/shared/components/ui/input";
import { Kbd } from "@/shared/components/ui/kbd";
import { ScrollArea } from "@/shared/components/ui/scroll-area";
import { useDebugMode } from "@/shared/hooks/queries/useDebugMode";
import { useSimulationSettings } from "@/shared/hooks/queries/useSimulationSettings";
import { cn } from "@/shared/lib/utils";
import { useRunDebugCommand } from "../hooks/mutations/useRunDebugCommand";
import { useDebugCommands } from "../hooks/queries/useDebugCommands";
import { applyCompletion, completionOf } from "../lib/completion";
import { stepHistory } from "../lib/history";
import { isToggleKey } from "../lib/toggle-key";

type LogKind = "input" | "result" | "error";

interface LogLine {
  readonly id: number;
  readonly kind: LogKind;
  readonly text: string;
}

const MAX_SUGGESTIONS = 12;

const WELCOME = "Console do modo debug. help lista os comandos; Tab completa; as setas voltam nos comandos enviados.";

/** Console de comandos do modo debug: só existe para o host com o servidor em modo debug. */
export function DebugConsole() {
  const debug = useDebugMode();
  return debug ? <HostConsole /> : null;
}

function HostConsole() {
  const { data: settings } = useSimulationSettings();
  return settings?.is_host ? <ConsolePanel /> : null;
}

function ConsolePanel() {
  const [open, setOpen] = useState(false);
  const [line, setLine] = useState("");
  const [log, setLog] = useState<readonly LogLine[]>([{ id: 0, kind: "result", text: WELCOME }]);
  const [sent, setSent] = useState<readonly string[]>([]);
  const [cursor, setCursor] = useState(0);
  const nextId = useRef(1);
  const end = useRef<HTMLDivElement>(null);

  const { data: catalog } = useDebugCommands(open);
  const run = useRunDebugCommand();
  const completion = completionOf(line, catalog?.commands ?? []);

  // A tecla do console abre e fecha de qualquer tela, exceto enquanto outro campo recebe texto
  useEffect(() => {
    function onKeyDown(event: globalThis.KeyboardEvent) {
      if (!isToggleKey(event) || event.ctrlKey || event.metaKey || event.altKey) return;
      const target = event.target;
      const typing =
        target instanceof HTMLElement &&
        (target.isContentEditable || target.matches("input, textarea, select")) &&
        target.dataset.slot !== "debug-console-input";
      if (typing) return;
      event.preventDefault();
      setOpen((current) => !current);
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  // O log rola até a última linha
  useEffect(() => {
    end.current?.scrollIntoView({ block: "end" });
  }, [log, open]);

  function append(kind: LogKind, text: string) {
    const entry = { id: nextId.current++, kind, text };
    setLog((current) => [...current, entry]);
  }

  function submit() {
    const command = line.trim();
    if (!command) return;
    append("input", `> ${command}`);
    const history = sent.at(-1) === command ? sent : [...sent, command];
    setSent(history);
    setCursor(history.length);
    setLine("");
    run.mutate(command, {
      onSuccess: (result) => append("result", result.message),
      onError: (error) => append("error", error.message),
    });
  }

  function onKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (isToggleKey(event.nativeEvent) || event.key === "Escape") {
      event.preventDefault();
      setOpen(false);
      return;
    }
    if (event.key === "Enter") {
      event.preventDefault();
      submit();
    } else if (event.key === "Tab") {
      event.preventDefault();
      setLine(applyCompletion(line, completion));
    } else if (event.key === "ArrowUp" || event.key === "ArrowDown") {
      event.preventDefault();
      const step = stepHistory(sent, cursor, event.key === "ArrowUp" ? "up" : "down");
      setCursor(step.cursor);
      setLine(step.line);
    }
  }

  if (!open) return null;

  return (
    <section
      aria-label="Console do modo debug"
      className="fixed inset-x-0 bottom-0 z-50 flex flex-col border-t bg-card shadow-lg"
    >
      {/* Saída dos comandos */}
      <ScrollArea className="h-56">
        <div className="grid gap-0.5 px-4 py-3 font-mono text-[13px] whitespace-pre-wrap">
          {log.map((entry) => (
            <p
              key={entry.id}
              className={cn(
                entry.kind === "input" && "text-muted-foreground",
                entry.kind === "error" && "text-destructive",
              )}
            >
              {entry.text}
            </p>
          ))}
          <div ref={end} />
        </div>
      </ScrollArea>

      {/* Escolhas para a palavra em curso */}
      <div className="flex min-h-9 flex-wrap items-center gap-1.5 border-t px-4 py-1.5">
        {completion.options.slice(0, MAX_SUGGESTIONS).map((option) => (
          <Badge key={option.value} variant="secondary">
            {option.value}
            {option.label && <span className="font-sans text-muted-foreground">{option.label}</span>}
          </Badge>
        ))}
        {completion.options.length > MAX_SUGGESTIONS && (
          <span className="text-xs text-muted-foreground">+{completion.options.length - MAX_SUGGESTIONS}</span>
        )}
      </div>

      {/* Linha de comando */}
      <div className="flex items-center gap-3 border-t px-4 py-2">
        <Input
          autoFocus
          numeric
          fieldSize="sm"
          data-slot="debug-console-input"
          aria-label="Comando"
          placeholder="help"
          autoComplete="off"
          spellCheck={false}
          value={line}
          onChange={(event) => {
            setLine(event.target.value);
            setCursor(sent.length);
          }}
          onKeyDown={onKeyDown}
        />
        <span className="flex shrink-0 items-center gap-1.5 text-xs text-muted-foreground">
          <Kbd className="ml-0">Tab</Kbd> completa <Kbd className="ml-0">Esc</Kbd> fecha
        </span>
      </div>
    </section>
  );
}
