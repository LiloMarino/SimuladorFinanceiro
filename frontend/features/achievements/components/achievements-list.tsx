import { useState } from "react";
import { Link } from "react-router-dom";
import { ArrowDown, ArrowUp, Info, Medal, TrendingUp, X } from "lucide-react";
import { Alert, AlertAction, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Card } from "@/shared/components/ui/card";
import { ErrorState } from "@/shared/components/error-state";
import { Input } from "@/shared/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { cn } from "@/shared/lib/utils";
import type ApiError from "@/shared/lib/models/ApiError";
import type { Achievement } from "@/types";
import { progressFraction } from "../lib/format";
import { AchievementRow, ROW_GRID } from "./achievement-row";
import { AchievementsListSkeleton } from "./achievements-skeleton";

const PAGE_SIZE = 10;

type Tab = "all" | "unlocked" | "locked";

type AchievementsListProps = {
  /** Ausente enquanto a lista carrega ou quando ela falhou: as abas aparecem zeradas e apagadas */
  achievements?: Achievement[];
  error?: ApiError | null;
  onRetry: () => void;
  /** Nick do host, quando quem vê a tela é convidado na sala dele */
  guestOf?: string;
  /** Só com a partida em andamento há para onde levar o primeiro passo */
  canPlay: boolean;
};

/** Abas, busca e a lista de conquistas: as desbloqueadas pela data e, abaixo, o grupo das bloqueadas. */
export function AchievementsList({ achievements, error, onRetry, guestOf, canPlay }: AchievementsListProps) {
  const [tab, setTab] = useState<Tab>("all");
  const [search, setSearch] = useState("");
  const [newestFirst, setNewestFirst] = useState(true);
  const [showAll, setShowAll] = useState(false);
  const [noticeClosed, setNoticeClosed] = useState(false);

  const query = search.trim().toLowerCase();
  const matches = (a: Achievement) =>
    !query || [a.name, a.description].some((text) => text?.toLowerCase().includes(query));

  const all = achievements ?? [];
  const byUnlockDate = (a: Achievement, b: Achievement) =>
    (newestFirst ? -1 : 1) * (a.unlock?.unlocked_at ?? "").localeCompare(b.unlock?.unlocked_at ?? "");
  const unlockedRows = all.filter((a) => a.unlock && matches(a)).sort(byUnlockDate);
  // As bloqueadas com barra vêm primeiro, da mais adiantada para a menos
  const lockedRows = all
    .filter((a) => !a.unlock && matches(a))
    .sort(
      (a, b) => (b.progress ? progressFraction(b.progress) : -1) - (a.progress ? progressFraction(a.progress) : -1),
    );

  const rows = tab === "unlocked" ? unlockedRows : tab === "locked" ? lockedRows : [...unlockedRows, ...lockedRows];
  const visible = showAll ? rows : rows.slice(0, PAGE_SIZE);
  const visibleUnlocked = visible.filter((a) => a.unlock);
  const visibleLocked = visible.filter((a) => !a.unlock);
  const nothingUnlockedYet = achievements !== undefined && !all.some((a) => a.unlock);

  return (
    <Card size="flush">
      {/* Aviso do convidado */}
      {guestOf && !noticeClosed && (
        <div className="px-4.5 pt-4">
          <Alert variant="info">
            <Info />
            <AlertTitle>Estas são as suas conquistas na sala de {guestOf}</AlertTitle>
            <AlertDescription>
              Elas ficam salvas no computador de quem hospeda. As que você tem na sua própria sala não aparecem aqui, e
              as daqui não vão para lá.
            </AlertDescription>
            <AlertAction>
              <Button variant="outline" size="sm" aria-label="Fechar" onClick={() => setNoticeClosed(true)}>
                <X />
              </Button>
            </AlertAction>
          </Alert>
        </div>
      )}

      {/* Abas e busca */}
      <div
        className={cn(
          "flex items-center justify-between gap-3 border-b border-border px-4.5 py-3.5",
          achievements === undefined && "pointer-events-none opacity-55",
        )}
      >
        <Tabs value={tab} onValueChange={(value) => setTab(value as Tab)}>
          <TabsList>
            <TabsTrigger value="all">
              Todas <span className="font-mono text-faint-foreground">{all.length}</span>
            </TabsTrigger>
            <TabsTrigger value="unlocked">
              Desbloqueadas{" "}
              <span className="font-mono text-faint-foreground">{all.filter((a) => a.unlock).length}</span>
            </TabsTrigger>
            <TabsTrigger value="locked">
              Bloqueadas <span className="font-mono text-faint-foreground">{all.filter((a) => !a.unlock).length}</span>
            </TabsTrigger>
          </TabsList>
        </Tabs>
        <Input
          fieldSize="sm"
          className="w-55"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar conquista"
          aria-label="Buscar conquista"
        />
      </div>

      {/* Cabeçalho da tabela */}
      <div
        className={cn(
          ROW_GRID,
          "border-b border-border bg-subtle py-2 text-xs font-medium text-muted-foreground",
          achievements === undefined && "opacity-55",
        )}
      >
        <span />
        <span>Conquista</span>
        <span>Categoria</span>
        <button
          type="button"
          className="inline-flex items-center justify-end gap-1 hover:text-foreground"
          onClick={() => setNewestFirst((prev) => !prev)}
        >
          Desbloqueada em {newestFirst ? <ArrowDown className="size-3" /> : <ArrowUp className="size-3" />}
        </button>
      </div>

      {error && achievements === undefined ? (
        <>
          <div className="px-4.5 py-4">
            <ErrorState
              title="Não deu para carregar as conquistas"
              description="O servidor do host não respondeu. Suas conquistas continuam salvas; é só a lista que não veio."
              error={error}
              onRetry={onRetry}
            />
          </div>
          <div className="opacity-50">
            <AchievementsListSkeleton />
          </div>
        </>
      ) : achievements === undefined ? (
        <AchievementsListSkeleton />
      ) : (
        <>
          {nothingUnlockedYet && !query && tab !== "locked" && (
            <div className="mx-4.5 my-4 flex items-center gap-4 rounded-xl border border-border bg-card px-4.5 py-4">
              <span className="inline-flex size-12 shrink-0 items-center justify-center rounded-xl bg-muted text-toast-muted [&>svg]:size-6">
                <Medal />
              </span>
              <div className="grid min-w-0 flex-1 gap-0.5">
                <strong>Nenhuma conquista ainda</strong>
                <span className="text-[13px] text-muted-foreground">
                  A primeira costuma vir da primeira compra. Escolha uma ação em Renda variável e compre qualquer
                  quantidade.
                </span>
              </div>
              {canPlay && (
                <Button nativeButton={false} render={<Link to="/variable-income" />}>
                  <TrendingUp />
                  Ir para Renda variável
                </Button>
              )}
            </div>
          )}

          {rows.length === 0 && query ? (
            <div className="mx-4.5 my-5 grid justify-items-center gap-1.5 rounded-[10px] border border-dashed border-input px-5 py-6.5 text-center">
              <span className="font-semibold">
                Nenhuma conquista encontrada para “<strong>{search.trim()}</strong>”.
              </span>
              <span className="text-[13px] text-muted-foreground">
                A busca olha nome e descrição. Tente “bilhão” ou outra palavra.
              </span>
              <Button variant="outline" size="sm" className="mt-1.5" onClick={() => setSearch("")}>
                Limpar busca
              </Button>
            </div>
          ) : (
            <>
              {visibleUnlocked.length > 0 && (
                <ul>
                  {visibleUnlocked.map((a) => (
                    <AchievementRow key={a.code} achievement={a} />
                  ))}
                </ul>
              )}
              {visibleLocked.length > 0 && (
                <>
                  {tab === "all" && (
                    <div className="border-b border-muted bg-subtle px-4.5 py-2 text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">
                      Bloqueadas · {lockedRows.length}
                    </div>
                  )}
                  <ul>
                    {visibleLocked.map((a) => (
                      <AchievementRow key={a.code} achievement={a} />
                    ))}
                  </ul>
                </>
              )}
            </>
          )}

          {rows.length > PAGE_SIZE && (
            <div className="flex items-center justify-between border-t border-muted px-4.5 py-3 text-[13px] text-muted-foreground">
              <span>
                Mostrando {visible.length} de {rows.length}
              </span>
              <Button variant="outline" size="sm" onClick={() => setShowAll((prev) => !prev)}>
                {showAll ? "Mostrar menos" : "Mostrar todas"}
              </Button>
            </div>
          )}
        </>
      )}
    </Card>
  );
}
