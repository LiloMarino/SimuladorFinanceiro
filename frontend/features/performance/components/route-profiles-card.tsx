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

/**
 * Liga o perfil das rotas. Cada rota guarda as 3 requisições mais lentas; a média é dessas 3, o
 * pior caso da rota.
 */
export function RouteProfilesCard() {
  const { data } = useRouteProfiles();
  const toggle = useSetRouteProfiles();
  const enabled = data?.enabled ?? false;
  const routes = data?.routes ?? [];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Perfil das rotas</CardTitle>
        <CardDescription>
          Ligado, cada requisição às rotas do jogo grava o tempo de cada função que ela executou, só dela, num arquivo
          para abrir no snakeviz. Cada rota guarda as 3 requisições mais lentas, e a média é só dessas 3: o pior caso da
          rota. O tempo de sempre dela está em &quot;Tempo gasto por rota ou evento&quot;. Enquanto ligado, o servidor
          responde mais devagar: o perfil mostra as proporções, não os milissegundos.
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
              <TableHead className="text-right">Média das lentas</TableHead>
              <TableHead>Requisições mais lentas (para abrir)</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {routes.map((group) => {
              const average =
                group.profiles.reduce((sum, profile) => sum + profile.duration_ms, 0) / group.profiles.length;
              return (
                <TableRow key={group.route}>
                  <TableCell>
                    <code className="font-mono text-[12.5px]">{group.route}</code>
                  </TableCell>
                  <TableCell className="text-right">
                    {displayDuration(average)} <span className="text-muted-foreground">de {group.profiles.length}</span>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-3">
                      {group.profiles.map((profile) => (
                        <div key={profile.id} className="flex items-center gap-1.5">
                          <span title={new Date(profile.created_at).toLocaleTimeString("pt-BR")}>
                            {displayDuration(profile.duration_ms)}
                          </span>
                          <CopyButton text={`pnpm profile:view ${profile.file}`} variant="outline" />
                        </div>
                      ))}
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
            {routes.length === 0 && (
              <TableEmptyRow colSpan={3}>
                <span className="text-muted-foreground">
                  {enabled
                    ? "Use o jogo: as rotas que você tocar aparecem aqui."
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
