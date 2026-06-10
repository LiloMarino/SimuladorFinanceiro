import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/shared/components/ui/dialog";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/shared/components/ui/form";
import { Input } from "@/shared/components/ui/input";
import { formatMoney } from "@/shared/lib/utils/format";
import type { UseFormReturn } from "react-hook-form";
import type { SimulationFormValues } from "./lobby-simulation-form";

interface LobbySettingsDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  form: UseFormReturn<SimulationFormValues>;
  isHost: boolean;
  loading: boolean;
}

export function LobbySettingsDialog({ open, onOpenChange, form, isHost, loading }: LobbySettingsDialogProps) {
  const disableFields = loading || !isHost;

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
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
