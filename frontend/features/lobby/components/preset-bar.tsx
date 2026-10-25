import { useState } from "react";
import { useWatch, type UseFormReturn } from "react-hook-form";
import { Bookmark, BookmarkPlus, Check, ChevronDown, Lock, Pencil, RefreshCw, TriangleAlert } from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/shared/components/ui/dropdown-menu";
import { Skeleton } from "@/shared/components/ui/skeleton";
import type { AppliedPreset, Preset, SimulationSettingsData } from "@/types";
import { useLoadPreset } from "../hooks/mutations/useLoadPreset";
import { useUpdatePresetRules } from "../hooks/mutations/useUpdatePresetRules";
import { usePresets } from "../hooks/queries/usePresets";
import { changedGroups, lowercaseGroups, presetSummary } from "../lib/preset";
import { toSettingsBody } from "../lib/simulation-form";
import { ManagePresetsDialog } from "./manage-presets-dialog";
import type { SimulationFormValues } from "./lobby-match";
import { SavePresetDialog } from "./save-preset-dialog";

type PresetBarProps = {
  form: UseFormReturn<SimulationFormValues>;
  isHost: boolean;
  /** Regras de uma partida salva: carregar fica desligado, salvar como preset continua */
  locked: boolean;
  /** O preset de onde vieram as regras da nova partida, com o que mudou desde que foi carregado */
  applied: AppliedPreset | null;
  /** As regras que o servidor gravou ao carregar um preset entram no formulário */
  onApplyLoaded: (settings: SimulationSettingsData) => void;
};

/** Faixa do painel de regras: de qual preset vêm as regras, a troca de preset e o salvar. */
export function PresetBar({ form, isHost, locked, applied, onApplyLoaded }: PresetBarProps) {
  if (!isHost) return locked || !applied ? null : <GuestPresetBar applied={applied} />;
  return <HostPresetBar form={form} locked={locked} applied={locked ? null : applied} onApplyLoaded={onApplyLoaded} />;
}

const STRIP = "flex flex-col gap-2 border-b bg-subtle px-6 py-3";
const LABEL = "shrink-0 text-xs font-medium text-muted-foreground";

function GuestPresetBar({ applied }: { applied: AppliedPreset }) {
  return (
    <div className={STRIP}>
      <div className="flex items-center gap-2">
        <span className={LABEL}>Preset</span>
        <span className="flex min-w-0 items-center gap-1.5 text-[13px]">
          <Bookmark className="size-3.5 shrink-0 text-primary" />
          <b className="truncate font-semibold">{applied.name}</b>
          {applied.changed.length > 0 && (
            <Badge variant="warning" size="sm">
              modificado
            </Badge>
          )}
        </span>
        <span className="ml-auto shrink-0 text-xs text-muted-foreground">O host escolhe as regras</span>
      </div>
    </div>
  );
}

type HostPresetBarProps = Pick<PresetBarProps, "form" | "locked" | "onApplyLoaded"> & { applied: AppliedPreset | null };

function HostPresetBar({ form, locked, applied, onApplyLoaded }: HostPresetBarProps) {
  const values = useWatch({ control: form.control }) as SimulationFormValues;
  const [saveOpen, setSaveOpen] = useState(false);
  const [manageOpen, setManageOpen] = useState(false);
  const presets = usePresets();
  const { mutate: load } = useLoadPreset();
  const { mutate: overwrite, isPending: overwriting } = useUpdatePresetRules();

  const builtIn = (presets.data ?? []).filter((preset) => preset.built_in);
  const mine = (presets.data ?? []).filter((preset) => !preset.built_in);
  const changed = applied?.changed ?? [];
  // Uma partida em edição só vira preset com todos os campos válidos; a salva já foi validada
  const canSave = locked || form.formState.isValid;

  const loadPreset = (preset: Preset) =>
    load(preset.id, {
      onSuccess: ({ settings, defaulted }) => {
        onApplyLoaded(settings);
        toast.success(
          <span>
            Regras do <b>{preset.name}</b> aplicadas. Todos na sala já veem.
          </span>,
          {
            description:
              defaulted.length > 0
                ? `Salvo antes de ${lowercaseGroups(defaulted)}: ${defaulted.length === 1 ? "veio" : "vieram"} do padrão.`
                : undefined,
          },
        );
      },
    });

  const overwriteApplied = () => {
    if (!applied) return;
    overwrite(
      { presetId: applied.id, rules: toSettingsBody(values) },
      {
        onSuccess: () =>
          toast.success(
            <span>
              Alterações salvas em <b>{applied.name}</b>
            </span>,
          ),
      },
    );
  };

  return (
    <div className={STRIP}>
      <div className="flex items-center gap-2">
        <span className={LABEL}>Preset</span>

        {/* Seletor */}
        <DropdownMenu>
          <DropdownMenuTrigger disabled={locked} render={<Button variant="field" className="min-w-0 flex-1" />}>
            {applied ? (
              <>
                <Bookmark className="text-primary" />
                <b className="truncate font-semibold">{applied.name}</b>
                {changed.length > 0 && (
                  <Badge variant="warning" size="sm">
                    modificado
                  </Badge>
                )}
              </>
            ) : (
              <span className="truncate text-muted-foreground">Escolher um preset</span>
            )}
            <ChevronDown className="ml-auto text-muted-foreground" />
          </DropdownMenuTrigger>

          <DropdownMenuContent align="start" className="w-110 max-w-[calc(100vw-2rem)]">
            {presets.isPending && <PresetListSkeleton />}
            {presets.isError && (
              <div className="flex items-center gap-2.5 px-3 py-3.5 text-[13px]">
                <TriangleAlert className="size-4 shrink-0 text-destructive" />
                <span className="flex-1">Não deu para carregar os presets.</span>
                <Button variant="outline" size="sm" onClick={() => void presets.refetch()}>
                  <RefreshCw />
                  Tentar de novo
                </Button>
              </div>
            )}
            {presets.data && (
              <>
                <MenuHeader hint="· não se apagam">Prontos</MenuHeader>
                {builtIn.map((preset) => (
                  <PresetItem
                    key={preset.id}
                    preset={preset}
                    selected={applied?.id === preset.id}
                    onSelect={loadPreset}
                  />
                ))}
                <DropdownMenuSeparator />
                <MenuHeader>Meus presets</MenuHeader>
                {mine.map((preset) => (
                  <PresetItem
                    key={preset.id}
                    preset={preset}
                    selected={applied?.id === preset.id}
                    onSelect={loadPreset}
                  />
                ))}
                {mine.length === 0 && (
                  <div className="py-1.5 pr-2.5 pb-2.5 pl-8.5 text-xs text-muted-foreground">
                    Nenhum ainda. Monte as regras e use <b className="text-foreground">Salvar como preset</b>.
                  </div>
                )}
                {mine.length > 0 && (
                  <>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem variant="action" onClick={() => setManageOpen(true)}>
                      Renomear ou apagar meus presets…
                      <Pencil className="ml-auto" />
                    </DropdownMenuItem>
                  </>
                )}
              </>
            )}
          </DropdownMenuContent>
        </DropdownMenu>

        {changed.length === 0 && (
          <Button variant="outline" size="sm" disabled={!canSave} onClick={() => setSaveOpen(true)}>
            <BookmarkPlus />
            Salvar como preset
          </Button>
        )}
      </div>

      {/* O que mudou depois de carregar */}
      {applied && changed.length > 0 && (
        <div className="flex items-center gap-2 pl-12.5">
          <span className="min-w-0 flex-1 text-xs text-muted-foreground">
            Mudou desde que carregou: {changedGroups(changed)}
          </span>
          {!applied.built_in && (
            <Button size="sm" disabled={!canSave || overwriting} onClick={overwriteApplied}>
              Salvar alterações
            </Button>
          )}
          <Button variant="outline" size="sm" disabled={!canSave} onClick={() => setSaveOpen(true)}>
            Salvar como novo
          </Button>
        </div>
      )}

      <SavePresetDialog open={saveOpen} onOpenChange={setSaveOpen} values={values} rules={toSettingsBody(values)} />
      {/* Sem presets do host não há o que gerenciar: apagar o último fecha o diálogo */}
      <ManagePresetsDialog open={manageOpen && mine.length > 0} onOpenChange={setManageOpen} presets={mine} />
    </div>
  );
}

function MenuHeader({ children, hint }: { children: string; hint?: string }) {
  return (
    <div className="flex items-center gap-1.5 px-2.5 pt-2 pb-1 text-[11px] font-semibold tracking-[.06em] text-faint-foreground uppercase">
      {children}
      {hint && <span className="font-medium tracking-normal normal-case">{hint}</span>}
    </div>
  );
}

type PresetItemProps = { preset: Preset; selected: boolean; onSelect: (preset: Preset) => void };

function PresetItem({ preset, selected, onSelect }: PresetItemProps) {
  return (
    <DropdownMenuItem size="rich" variant={selected ? "selected" : "default"} onClick={() => onSelect(preset)}>
      {selected ? <Check className="mt-0.5 text-primary" /> : <span className="w-3.5 shrink-0" />}
      <span className="grid min-w-0 flex-1 gap-px">
        <b className="font-semibold wrap-break-word">{preset.name}</b>
        <span className="text-xs text-muted-foreground">{presetSummary(preset)}</span>
      </span>
      {preset.built_in && <Lock className="mt-1 text-faint-foreground" />}
    </DropdownMenuItem>
  );
}

/** Esqueleto no formato dos itens: o nome e uma linha de resumo */
function PresetListSkeleton() {
  return (
    <>
      {[0, 1, 2, 3].map((row) => (
        <div key={row} className="flex gap-2.5 px-2.5 py-2">
          <span className="w-3.5 shrink-0" />
          <div className="grid gap-1.5">
            <Skeleton className="h-3 w-30" />
            <Skeleton className="h-2.5 w-75" />
          </div>
        </div>
      ))}
    </>
  );
}
