import { type ReactNode, useState } from "react";
import { Gavel, TriangleAlert } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import {
  Dialog,
  DialogBody,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { Field, FieldDescription, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { useAuth } from "@/shared/hooks/useAuth";
import { normalizeNumberString } from "@/shared/lib/utils";
import { displayDayMonth, displayList } from "@/shared/lib/utils/display";
import { formatMoney } from "@/shared/lib/utils/format";
import type { GovernmentPanel, MeasureKind, ProposeMeasureRequest } from "@/types";
import { useProposeMeasure } from "../hooks/mutations/useProposeMeasure";
import { useMeasurePreview } from "../hooks/queries/useMeasurePreview";
import { VALUE_INFO, signedPoints as signedProfilePoints } from "../lib/voters";
import {
  GENERAL_KINDS,
  type GeneralKind,
  generalLabel,
  holdingLabel,
  impactSentence,
  isGeneral,
  percentLabel,
  rateToFraction,
  signedPoints,
} from "../lib/government";

type Mode = "general" | "sector";
type ExemptionRule = "keep" | "end" | "change";
type SectorChange = "tax" | "exempt";

const WHOLE_SECTOR = "all";

/** Escolhe a opção de um grupo de uma só opção: soltar a marcada não muda nada. */
const pick =
  <T extends string>(set: (value: T) => void) =>
  (values: string[]) => {
    if (values[0]) set(values[0] as T);
  };

type NewMeasureDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  panel: GovernmentPanel;
  /** O imposto que "Mudar" pré-seleciona; sem ele a medida nasce no primeiro imposto sem pendência */
  initialKind?: MeasureKind | undefined;
};

/** Propor uma medida ao Congresso: um imposto geral ou a regra de um setor ou segmento. */
export function NewMeasureDialog({ open, onOpenChange, panel, initialKind }: NewMeasureDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-120">
        <DialogHeader variant="divided">
          <DialogTitle>Nova medida</DialogTitle>
          <DialogDescription>Entra na fila do Congresso; a sala vê a fila.</DialogDescription>
        </DialogHeader>
        <MeasureForm panel={panel} initialKind={initialKind} onClose={() => onOpenChange(false)} />
      </DialogContent>
    </Dialog>
  );
}

type MeasureFormProps = {
  panel: GovernmentPanel;
  initialKind?: MeasureKind | undefined;
  onClose: () => void;
};

function MeasureForm({ panel, initialKind, onClose }: MeasureFormProps) {
  const { user } = useAuth();
  const propose = useProposeMeasure();
  const pendingKinds = new Set(panel.taxes.filter((row) => row.pending).map((row) => row.kind));
  const firstFree = GENERAL_KINDS.find((kind) => !pendingKinds.has(kind)) ?? GENERAL_KINDS[0];

  const [mode, setMode] = useState<Mode>(initialKind && !isGeneral(initialKind) ? "sector" : "general");
  const [kind, setKind] = useState<GeneralKind>(initialKind && isGeneral(initialKind) ? initialKind : firstFree);
  const [rule, setRule] = useState<ExemptionRule>("keep");
  const [valueText, setValueText] = useState("");
  const [sector, setSector] = useState(panel.sectors[0]?.name ?? "");
  const [segment, setSegment] = useState(WHOLE_SECTOR);
  const [change, setChange] = useState<SectorChange>("tax");
  const [pointsText, setPointsText] = useState("");

  const generalRows = panel.taxes.filter((tax): tax is typeof tax & { kind: GeneralKind } => isGeneral(tax.kind));
  const row = generalRows.find((candidate) => candidate.kind === kind);
  const option = panel.sectors.find((candidate) => candidate.name === sector);
  const segmentOption = option?.segments.find((candidate) => candidate.name === segment);

  const request = buildRequest({ mode, kind, rule, valueText, sector, segment, change, pointsText });
  const preview = useMeasurePreview(request);
  // A prévia anterior fica à vista enquanto a nova carrega, mas some quando o pedido deixa de estar completo
  const data = request && !preview.isError ? preview.data : undefined;

  return (
    <>
      <DialogBody>
        <div className="grid gap-3.5">
          <ToggleGroup
            variant="segmented"
            aria-label="Tipo de medida"
            className="w-full"
            value={[mode]}
            onValueChange={pick<Mode>(setMode)}
          >
            <ToggleGroupItem value="general" className="flex-1">
              Imposto geral
            </ToggleGroupItem>
            <ToggleGroupItem value="sector" className="flex-1">
              Por setor
            </ToggleGroupItem>
          </ToggleGroup>

          {mode === "general" && row && (
            <>
              <Field>
                <FieldLabel>Imposto</FieldLabel>
                <Select
                  value={kind}
                  items={Object.fromEntries(generalRows.map((tax) => [tax.kind, generalLabel(tax.kind, tax.value)]))}
                  onValueChange={(value) => {
                    if (!value) return;
                    setKind(value);
                    setRule("keep");
                    setValueText("");
                  }}
                >
                  <SelectTrigger size="lg" className="w-full" aria-label="Imposto">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {generalRows.map((tax) => (
                      <SelectItem key={tax.kind} value={tax.kind} disabled={pendingKinds.has(tax.kind)}>
                        {generalLabel(tax.kind, tax.value)}
                        {pendingKinds.has(tax.kind) && " · já tem medida a caminho"}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </Field>

              {kind === "STOCK_EXEMPTION" ? (
                <>
                  <Field>
                    <FieldLabel>Nova regra</FieldLabel>
                    <ToggleGroup
                      variant="segmented"
                      aria-label="Nova regra"
                      value={[rule]}
                      onValueChange={pick<ExemptionRule>(setRule)}
                    >
                      <ToggleGroupItem value="keep">Mantém</ToggleGroupItem>
                      <ToggleGroupItem value="end">Acaba</ToggleGroupItem>
                      <ToggleGroupItem value="change">Muda o limite</ToggleGroupItem>
                    </ToggleGroup>
                  </Field>
                  {rule === "change" && (
                    <Field>
                      <FieldLabel htmlFor="measure-limit">Novo limite por mês</FieldLabel>
                      <Input
                        id="measure-limit"
                        numeric
                        inputMode="decimal"
                        placeholder="R$ 0,00"
                        value={valueText}
                        onChange={(event) => setValueText(formatMoney(event.target.value))}
                      />
                    </Field>
                  )}
                </>
              ) : (
                <Field>
                  <FieldLabel htmlFor="measure-rate">
                    {kind === "FIXED_INCOME_TABLE" ? "Tabela única de (%)" : "Nova alíquota (%)"}
                  </FieldLabel>
                  <Input
                    id="measure-rate"
                    numeric
                    inputMode="decimal"
                    placeholder="Ex.: 22,5"
                    value={valueText}
                    onChange={(event) => setValueText(event.target.value)}
                  />
                  <FieldDescription>
                    Hoje{" "}
                    {kind === "FIXED_INCOME_TABLE"
                      ? `${percentLabel(row.top_value ?? row.value)} no topo`
                      : percentLabel(row.value)}
                    .
                  </FieldDescription>
                </Field>
              )}
            </>
          )}

          {mode === "sector" && (
            <>
              <Field>
                <FieldLabel>Setor</FieldLabel>
                <Select
                  value={sector}
                  items={Object.fromEntries(panel.sectors.map((candidate) => [candidate.name, candidate.name]))}
                  onValueChange={(value) => {
                    if (!value) return;
                    setSector(value);
                    setSegment(WHOLE_SECTOR);
                  }}
                >
                  <SelectTrigger size="lg" className="w-full" aria-label="Setor">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {panel.sectors.map((candidate) => (
                      <SelectItem key={candidate.name} value={candidate.name}>
                        {candidate.name} · {candidate.assets} ativos
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {option && (
                  <FieldDescription>
                    {displayList(option.tickers)}. Também dá para escolher só um segmento do setor.
                  </FieldDescription>
                )}
              </Field>

              {option && option.segments.length > 1 && (
                <Field>
                  <FieldLabel>Segmento</FieldLabel>
                  <Select
                    value={segment}
                    items={{
                      [WHOLE_SECTOR]: "O setor inteiro",
                      ...Object.fromEntries(option.segments.map((candidate) => [candidate.name, candidate.name])),
                    }}
                    onValueChange={(value) => value && setSegment(value)}
                  >
                    <SelectTrigger size="lg" className="w-full" aria-label="Segmento">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={WHOLE_SECTOR}>O setor inteiro · {option.assets} ativos</SelectItem>
                      {option.segments.map((candidate) => (
                        <SelectItem key={candidate.name} value={candidate.name}>
                          {candidate.name} · {candidate.assets} ativos
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {segmentOption && (
                    <FieldDescription>
                      Só os {segmentOption.assets} ativos desse segmento entram na medida.
                    </FieldDescription>
                  )}
                </Field>
              )}

              <div className="grid grid-cols-2 gap-3">
                <Field>
                  <FieldLabel>Mudança</FieldLabel>
                  <ToggleGroup
                    variant="segmented"
                    aria-label="Mudança"
                    value={[change]}
                    onValueChange={pick<SectorChange>(setChange)}
                  >
                    <ToggleGroupItem value="tax">Taxar a mais</ToggleGroupItem>
                    <ToggleGroupItem value="exempt">Isentar</ToggleGroupItem>
                  </ToggleGroup>
                </Field>
                <Field>
                  <FieldLabel htmlFor="measure-points">Quanto (pontos)</FieldLabel>
                  <Input
                    id="measure-points"
                    numeric
                    inputMode="decimal"
                    placeholder={change === "exempt" ? "—" : "Ex.: 5"}
                    disabled={change === "exempt"}
                    value={change === "exempt" ? "" : pointsText}
                    onChange={(event) => setPointsText(event.target.value)}
                  />
                  <FieldDescription>
                    {change === "exempt"
                      ? `${percentLabel(panel.taxes.find((tax) => tax.kind === "STOCK_PROFIT_RATE")?.value ?? 0)} → 0% nas vendas com lucro.`
                      : "Pontos somados à alíquota das vendas com lucro."}
                  </FieldDescription>
                </Field>
              </div>
            </>
          )}

          {preview.isError && (
            <Alert variant="destructive">
              <TriangleAlert />
              <AlertTitle>Essa medida não dá para enviar</AlertTitle>
              <AlertDescription>{preview.error.message}</AlertDescription>
            </Alert>
          )}

          {data && (
            <>
              <dl className="grid divide-y rounded-lg border px-3 text-[13px]">
                {mode === "sector" && (
                  <Row label="Quem tem esses ativos">
                    {data.holdings.length > 0
                      ? data.holdings.map((holding) => holdingLabel(holding, user?.nickname)).join(" · ")
                      : "ninguém"}
                  </Row>
                )}
                <Row label="Aprovação, ao valer">{signedPoints(data.impact)}</Row>
                <Row label="Perfil do partido, se aprovada">
                  {data.profile_moves.length > 0
                    ? data.profile_moves
                        .map((move) => `${signedProfilePoints(Number(move.points))} ${VALUE_INFO[move.value].label}`)
                        .join(" · ")
                    : "não muda"}
                </Row>
              </dl>
              <p className="text-xs leading-normal text-muted-foreground">{impactSentence(data)}</p>
              <Alert variant="info">
                <Gavel />
                <AlertTitle>O Congresso vota em {displayDayMonth(data.vote_date)}</AlertTitle>
                <AlertDescription>
                  Passa com {data.chance}% de chance, a aprovação de hoje. Aprovada, vale em{" "}
                  {displayDayMonth(data.effective)}, {panel.vigence_days} dias depois.
                </AlertDescription>
              </Alert>
            </>
          )}

          {propose.isError && (
            <Alert variant="destructive">
              <TriangleAlert />
              <AlertTitle>Não deu para enviar a medida</AlertTitle>
              <AlertDescription>
                {propose.error.message}
                <Button
                  size="xs"
                  variant="outline"
                  className="ml-1.5"
                  disabled={!request || propose.isPending}
                  onClick={() => request && propose.mutate(request, { onSuccess: onClose })}
                >
                  Tentar de novo
                </Button>
              </AlertDescription>
            </Alert>
          )}
        </div>
      </DialogBody>

      <DialogFooter variant="divided" className="sm:data-[variant=divided]:justify-end">
        <Button variant="outline" onClick={onClose}>
          Cancelar
        </Button>
        <Button
          disabled={!request || !data || propose.isPending}
          onClick={() => request && propose.mutate(request, { onSuccess: onClose })}
        >
          Enviar ao Congresso
        </Button>
      </DialogFooter>
    </>
  );
}

function Row({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex justify-between gap-3 py-1.5">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="text-right font-mono font-semibold">{children}</dd>
    </div>
  );
}

type Draft = {
  mode: Mode;
  kind: GeneralKind;
  rule: ExemptionRule;
  valueText: string;
  sector: string;
  segment: string;
  change: SectorChange;
  pointsText: string;
};

/** O pedido que o rascunho forma; nulo enquanto falta o valor, e a prévia só roda com pedido completo. */
function buildRequest(draft: Draft): ProposeMeasureRequest | null {
  if (draft.mode === "sector") {
    if (!draft.sector) return null;
    const segment = draft.segment === WHOLE_SECTOR ? null : draft.segment;
    if (draft.change === "exempt") return { kind: "SECTOR_EXEMPT", sector: draft.sector, segment };
    const points = rateToFraction(draft.pointsText);
    return points ? { kind: "SECTOR_TAX", value: points, sector: draft.sector, segment } : null;
  }
  if (draft.kind === "STOCK_EXEMPTION") {
    if (draft.rule === "end") return { kind: draft.kind, value: "0" };
    const limit = normalizeNumberString(draft.valueText);
    return draft.rule === "change" && Number(limit) > 0 ? { kind: draft.kind, value: limit } : null;
  }
  const rate = rateToFraction(draft.valueText);
  return rate ? { kind: draft.kind, value: rate } : null;
}
