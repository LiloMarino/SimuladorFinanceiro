import { Card, CardAction, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Label } from "@/shared/components/ui/label";
import { Switch } from "@/shared/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableEmptyRow,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";
import { displayDuration } from "@/shared/lib/utils/display";
import { useSetRouteProfiles } from "../hooks/mutations/useSetRouteProfiles";
import { useRouteProfiles } from "../hooks/queries/useRouteProfiles";
import { CopyButton } from "./copy-button";

/** Liga o perfil das rotas: cada requisição à API vira um perfil, listado aqui. */
export function RouteProfilesCard() {
  const { data } = useRouteProfiles();
  const toggle = useSetRouteProfiles();
  const enabled = data?.enabled ?? false;
  const items = data?.items ?? [];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Perfil das rotas</CardTitle>
        <CardDescription>
          Ligado, cada requisição às rotas do jogo grava o tempo de cada função que ela executou, só dela, num arquivo
          para abrir no snakeviz. Enquanto ligado, o servidor responde mais devagar: o perfil mostra as proporções, não
          os milissegundos.
        </CardDescription>
        <CardAction>
          <div className="flex items-center gap-2">
            <Switch
              id="route-profiles"
              checked={enabled}
              disabled={!data || toggle.isPending}
              onCheckedChange={(value) => toggle.mutate(value)}
            />
            <Label htmlFor="route-profiles">{enabled ? "Gravando" : "Desligado"}</Label>
          </div>
        </CardAction>
      </CardHeader>

      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Rota</TableHead>
              <TableHead>Hora</TableHead>
              <TableHead className="text-right">Duração</TableHead>
              <TableHead>Para abrir</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {items.map((item) => {
              const command = `pnpm profile:view ${item.file}`;
              return (
                <TableRow key={item.id}>
                  <TableCell>
                    <code className="font-mono text-[12.5px]">{item.route}</code>
                  </TableCell>
                  <TableCell>{new Date(item.created_at).toLocaleTimeString("pt-BR")}</TableCell>
                  <TableCell className="text-right">{displayDuration(item.duration_ms)}</TableCell>
                  <TableCell>
                    <CopyButton text={command} variant="outline" />
                  </TableCell>
                </TableRow>
              );
            })}
            {items.length === 0 && (
              <TableEmptyRow colSpan={4}>
                <span className="text-muted-foreground">
                  {enabled
                    ? "Use o jogo: cada requisição às rotas aparece aqui."
                    : "Ligue o interruptor e use o jogo para gravar os perfis."}
                </span>
              </TableEmptyRow>
            )}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
