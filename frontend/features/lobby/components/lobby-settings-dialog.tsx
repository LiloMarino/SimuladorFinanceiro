import { useWatch, type UseFormReturn } from "react-hook-form";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/shared/components/ui/dialog";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/shared/components/ui/form";
import { Input } from "@/shared/components/ui/input";
import { Checkbox } from "@/shared/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { VICTORY_CRITERIA } from "@/shared/lib/victory-criteria";
import { InfoHint } from "@/shared/components/info-hint";
import { formatMoney, formatPositiveInteger } from "@/shared/lib/utils/format";
import type { SimulationFormValues } from "./lobby-simulation-form";
import type { CoverageCheck } from "../lib/coverage";
import { CoverageAlerts } from "./coverage-alerts";

interface LobbySettingsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  form: UseFormReturn<SimulationFormValues>;
  isHost: boolean;
  loading: boolean;
  coverageCheck: CoverageCheck;
}

export function LobbySettingsDialog({
  open,
  onOpenChange,
  form,
  isHost,
  loading,
  coverageCheck,
}: LobbySettingsDialogProps) {
  const disableFields = loading || !isHost;
  const priceImpactEnabled = useWatch({ control: form.control, name: "priceImpactEnabled" });

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Configurações da Simulação</DialogTitle>
          {!isHost && (
            <DialogDescription>Modo visualização — apenas o host pode editar.</DialogDescription>
          )}
        </DialogHeader>

        <Form {...form}>
          <form className="space-y-4">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome da Simulação</FormLabel>
                  <FormControl>
                    <Input placeholder="Ex: Simulação #1" {...field} disabled={disableFields} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="startDate"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Data Inicial</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} disabled={disableFields} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="endDate"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Data Final</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} disabled={disableFields} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <CoverageAlerts check={coverageCheck} />

            <FormField
              control={form.control}
              name="startingCash"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Saldo Inicial (R$)</FormLabel>
                  <FormControl>
                    <Input
                      inputMode="decimal"
                      placeholder="Saldo inicial da simulação"
                      {...field}
                      onChange={(e) => field.onChange(formatMoney(e.target.value))}
                      disabled={disableFields}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="monthlyContribution"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Aporte Mensal (R$)</FormLabel>
                  <FormControl>
                    <Input
                      inputMode="decimal"
                      placeholder="Aporte mensal da simulação"
                      {...field}
                      onChange={(e) => field.onChange(formatMoney(e.target.value))}
                      disabled={disableFields}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Critério de vitória */}
            <FormField
              control={form.control}
              name="victoryCriterion"
              render={({ field }) => (
                <FormItem>
                  <div className="flex items-center gap-2">
                    <FormLabel>Critério de vitória</FormLabel>
                    <InfoHint>
                      <div className="space-y-1 text-left">
                        {Object.values(VICTORY_CRITERIA).map((c) => (
                          <p key={c.label}>
                            <strong>{c.label}:</strong> {c.description}
                          </p>
                        ))}
                      </div>
                    </InfoHint>
                  </div>
                  <Select value={field.value} onValueChange={field.onChange} disabled={disableFields}>
                    <FormControl>
                      <SelectTrigger className="w-full">
                        <SelectValue />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {Object.entries(VICTORY_CRITERIA).map(([value, c]) => (
                        <SelectItem key={value} value={value}>
                          {c.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormDescription>Decide o pódio e a ordem do ranking.</FormDescription>
                </FormItem>
              )}
            />

            {/* Impacto de preço */}
            <FormField
              control={form.control}
              name="priceImpactEnabled"
              render={({ field }) => (
                <FormItem>
                  <div className="flex items-center gap-2">
                    <FormControl>
                      <Checkbox checked={field.value} onCheckedChange={field.onChange} disabled={disableFields} />
                    </FormControl>
                    <FormLabel>Impacto de preço das ordens</FormLabel>
                    <InfoHint>
                      Uma compra empurra o preço do ativo para cima nos pregões seguintes e uma venda empurra para
                      baixo. O desvio volta sozinho ao preço histórico se ninguém operar de novo. Desligado, os preços
                      seguem exatamente o histórico.
                    </InfoHint>
                  </div>
                  <FormDescription>Ordens grandes movem o preço dos dias seguintes.</FormDescription>
                </FormItem>
              )}
            />

            {priceImpactEnabled && (
              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="priceImpactK"
                  render={({ field }) => (
                    <FormItem>
                      <div className="flex items-center gap-2">
                        <FormLabel>Intensidade (k)</FormLabel>
                        <InfoHint>
                          Impacto = k × √(quantidade ÷ volume médio diário do ativo). Com k = 0,02, comprar 10% do volume
                          médio sobe o preço ~0,63%, e comprar o volume de um dia inteiro sobe ~2%. 0,02 é próximo do
                          mercado real; acima de 0,1 o efeito fica dramático.
                        </InfoHint>
                      </div>
                      <FormControl>
                        <Input inputMode="decimal" placeholder="Ex: 0,02" {...field} disabled={disableFields} />
                      </FormControl>
                      <FormDescription>Quanto uma ordem move o preço.</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="priceImpactDecayDays"
                  render={({ field }) => (
                    <FormItem>
                      <div className="flex items-center gap-2">
                        <FormLabel>Volta ao histórico (T)</FormLabel>
                        <InfoHint>
                          Por quantos pregões o desvio dura. O impacto vale cheio no pregão seguinte à ordem e cai pela
                          curva (1 − t/T)²: com T = 20, resta 64% no 5º pregão, 30% no 10º, 9% no 15º e some depois do
                          20º.
                        </InfoHint>
                      </div>
                      <FormControl>
                        <Input
                          inputMode="numeric"
                          placeholder="Ex: 20"
                          {...field}
                          onChange={(e) => field.onChange(formatPositiveInteger(e.target.value))}
                          disabled={disableFields}
                        />
                      </FormControl>
                      <FormDescription>Em pregões (dias úteis).</FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>
            )}
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
