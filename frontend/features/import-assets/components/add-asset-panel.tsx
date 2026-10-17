import { useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { CircleCheck, CircleX } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/shared/components/ui/alert-dialog";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Checkbox } from "@/shared/components/ui/checkbox";
import { Field, FieldContent, FieldDescription, FieldLabel } from "@/shared/components/ui/field";
import { Spinner } from "@/shared/components/ui/spinner";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { apiFetch } from "@/shared/lib/api/apiFetch";
import { toFormData } from "@/shared/lib/api/toFormData";
import { useApiMutation } from "@/shared/lib/api/useApiMutation";
import { queryKeys } from "@/shared/lib/queryKeys";
import { displayDate, parseLocalDate } from "@/shared/lib/utils/display";
import type { SeriesCoverage } from "@/types";
import { tickerFromFileName, type CsvInspection } from "../lib/csv-file";
import { CsvDropzone } from "./csv-dropzone";
import { TickerCombobox } from "./ticker-combobox";

type Source = "YFINANCE" | "CSV";
type ImportRequest = { source: Source; ticker: string; overwrite: boolean; file: File | null };

export const ADD_ASSET_INPUT_ID = "add-asset-ticker";
const ADD_ASSET_FILE_ID = "add-asset-file";

const formatIso = (iso: string) => displayDate(parseLocalDate(iso));

/** Importar uma ação: progresso, sucesso e erro aparecem aqui mesmo, sem toast. */
export function AddAssetPanel({ onClassify }: { onClassify: (ticker: string) => void }) {
  const queryClient = useQueryClient();
  const [source, setSource] = useState<Source>("YFINANCE");
  const [ticker, setTicker] = useState("");
  const [picked, setPicked] = useState<CsvInspection | null>(null);
  // O código vem do nome do arquivo até a pessoa digitar o seu
  const [tickerFromFile, setTickerFromFile] = useState(false);
  const [overwrite, setOverwrite] = useState(false);
  const [confirming, setConfirming] = useState(false);

  const importAsset = useApiMutation({
    mutationFn: (req: ImportRequest) =>
      req.source === "CSV"
        ? apiFetch<SeriesCoverage>("/api/import-assets/csv", {
            method: "POST",
            body: toFormData({ ticker: req.ticker, overwrite: req.overwrite, csv_file: req.file }),
          })
        : apiFetch<SeriesCoverage>("/api/import-assets/yfinance", {
            method: "POST",
            body: { ticker: req.ticker, overwrite: req.overwrite },
          }),
    onSettled: () => queryClient.invalidateQueries({ queryKey: queryKeys.seriesCoverage() }),
  });

  const file = picked && !picked.problem ? picked.file : null;
  const request: ImportRequest = { source, ticker: ticker.trim().toUpperCase(), overwrite, file };
  const ready = !!request.ticker && (source === "YFINANCE" || !!file);

  // Só confirma quando a importação vai trocar dado que já está na base
  const submit = () => (overwrite ? setConfirming(true) : importAsset.mutate(request));
  const startOver = () => {
    importAsset.reset();
    setTicker("");
    setPicked(null);
    setTickerFromFile(false);
  };

  const pickFile = (next: CsvInspection | null) => {
    setPicked(next);
    const fromName = next && !next.problem ? tickerFromFileName(next.file.name) : "";
    if (fromName && (!ticker.trim() || tickerFromFile)) {
      setTicker(fromName);
      setTickerFromFile(true);
    }
  };

  const imported = importAsset.data;
  const failedTicker = importAsset.variables?.ticker;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Adicionar ativo</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          {imported ? (
            <>
              <Alert variant="success">
                <CircleCheck />
                <AlertTitle>{imported.key} entrou na base</AlertTitle>
                <AlertDescription>
                  Dado real de {imported.start && formatIso(imported.start)} a{" "}
                  {imported.real_end && formatIso(imported.real_end)}
                  {imported.segment && ` · setor sugerido ${imported.segment.sector} · ${imported.segment.segment}`}
                  <br />
                  <Button variant="link" size="xs" onClick={() => onClassify(imported.key)}>
                    Conferir classificação →
                  </Button>
                </AlertDescription>
              </Alert>
              <Button variant="outline" onClick={startOver}>
                Importar outro
              </Button>
            </>
          ) : (
            <>
              <ToggleGroup
                variant="segmented"
                aria-label="Fonte dos preços"
                value={[source]}
                onValueChange={(values) => values[0] && setSource(values[0] as Source)}
              >
                <ToggleGroupItem value="YFINANCE">yFinance</ToggleGroupItem>
                <ToggleGroupItem value="CSV">Arquivo CSV</ToggleGroupItem>
              </ToggleGroup>

              {source === "CSV" && (
                <Field>
                  <FieldLabel htmlFor={ADD_ASSET_FILE_ID}>Arquivo</FieldLabel>
                  <CsvDropzone
                    id={ADD_ASSET_FILE_ID}
                    picked={picked}
                    disabled={importAsset.isPending}
                    onPick={pickFile}
                  />
                  <FieldDescription>
                    Colunas do Investing.com: <span className="font-mono">Data</span>,{" "}
                    <span className="font-mono">Último</span>, <span className="font-mono">Abertura</span>,{" "}
                    <span className="font-mono">Máxima</span>, <span className="font-mono">Mínima</span> e{" "}
                    <span className="font-mono">Vol.</span>
                  </FieldDescription>
                </Field>
              )}

              <Field>
                <FieldLabel htmlFor={ADD_ASSET_INPUT_ID}>Código do ativo</FieldLabel>
                <TickerCombobox
                  id={ADD_ASSET_INPUT_ID}
                  value={ticker}
                  onChange={(value) => {
                    setTicker(value);
                    setTickerFromFile(false);
                  }}
                  suggest={source === "YFINANCE"}
                  placeholder={source === "CSV" ? "Ex.: ITSA4" : "PETR4, VALE3, BTC-USD"}
                  invalid={importAsset.isError}
                  disabled={importAsset.isPending}
                />
                {source === "CSV" && tickerFromFile && (
                  <FieldDescription>Tirado do nome do arquivo; confira.</FieldDescription>
                )}
              </Field>

              <Field orientation="horizontal">
                <Checkbox
                  id="add-asset-overwrite"
                  checked={overwrite}
                  onCheckedChange={(checked) => setOverwrite(Boolean(checked))}
                  disabled={importAsset.isPending}
                />
                <FieldContent>
                  <FieldLabel htmlFor="add-asset-overwrite">Substituir o que já existe</FieldLabel>
                  <FieldDescription>Desmarcado, só entram pregões que ainda não estão na base.</FieldDescription>
                </FieldContent>
              </Field>

              {/* Importando: progresso no próprio painel */}
              {importAsset.isPending && (
                <div className="grid gap-1.5">
                  <span className="text-xs text-muted-foreground">
                    Baixando {request.ticker} {source === "CSV" ? "do arquivo" : "do yFinance"}…
                  </span>
                  <span className="h-1.5 overflow-hidden rounded-full bg-muted">
                    <span className="block h-full w-2/5 animate-pulse rounded-full bg-primary" />
                  </span>
                </div>
              )}

              {importAsset.isError && (
                <Alert variant="destructive">
                  <CircleX />
                  <AlertTitle>Não deu pra importar {failedTicker}</AlertTitle>
                  <AlertDescription>
                    {source === "YFINANCE"
                      ? "O yFinance não devolveu dados para esse código. Confira se está certo (na B3, o código é o mesmo da bolsa, ex.: PETR4)."
                      : "O arquivo não pôde ser lido. Confira as colunas e o formato das datas."}
                    <span className="mt-1 block font-mono text-[11px]">
                      Resposta do servidor: {importAsset.error.message}
                    </span>
                  </AlertDescription>
                </Alert>
              )}

              <Button disabled={!ready || importAsset.isPending} onClick={submit}>
                {importAsset.isPending && <Spinner />}
                {importAsset.isPending ? "Importando…" : importAsset.isError ? "Tentar de novo" : "Importar"}
              </Button>
            </>
          )}
        </div>
      </CardContent>

      <AlertDialog open={confirming} onOpenChange={setConfirming}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Substituir os dados de {request.ticker}?</AlertDialogTitle>
            <AlertDialogDescription>
              Os preços que já estão na base serão trocados pelos que vierem{" "}
              {source === "CSV" ? "do arquivo" : "do yFinance"}. Isso não pode ser desfeito.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => {
                setConfirming(false);
                importAsset.mutate(request);
              }}
            >
              Substituir
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </Card>
  );
}
