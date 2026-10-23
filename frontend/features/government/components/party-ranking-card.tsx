import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Table, TableBody, TableCell, TableHeader, TableRow } from "@/shared/components/ui/table";
import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { useTableSort } from "@/shared/hooks/useTableSort";
import { displayMoney } from "@/shared/lib/utils/display";
import type { OverviewReport } from "@/types";

export function PartyRankingCard({ report, currentPlayerName, final = false }: { report: OverviewReport; currentPlayerName?: string; final?: boolean }) {
  const parties = (report.parties ?? []).map((p, index) => ({ ...p, position: index + 1 }));
  const sorting = useTableSort(parties, { position: p => p.position, name: p => p.name, members: p => p.members.join(", "), wealth: p => Number(p.networth) });
  const winner = parties[0];
  return <Card><CardHeader><CardTitle>{final && report.party_ranking_decides && winner ? `${winner.name} venceu com ${displayMoney(winner.networth)}` : "Ranking de partidos"}</CardTitle>
    <CardDescription>{report.party_ranking_decides ? "Vitória pela soma dos patrimônios dos filiados. O ranking individual mantém os resultados financeiros de cada jogador." : "Comparação por patrimônio; o ranking individual decide a partida."}
      {winner?.members.includes(currentPlayerName ?? "") && report.party_ranking_decides && (final ? " Seu partido venceu." : " Seu partido lidera.")}</CardDescription></CardHeader>
    <CardContent><Table><TableHeader><TableRow>
      <SortableTableHead label="#" {...sorting.header("position")} /><SortableTableHead label="Partido" {...sorting.header("name")} /><SortableTableHead label="Filiados" {...sorting.header("members")} /><SortableTableHead label="Patrimônio somado" numeric {...sorting.header("wealth")} />
    </TableRow></TableHeader><TableBody>{sorting.rows.map(p => <TableRow key={p.party_id}><TableCell>{p.position}</TableCell><TableCell>{p.name}</TableCell><TableCell>{p.members.join(", ")}</TableCell><TableCell numeric>{displayMoney(p.networth)}</TableCell></TableRow>)}</TableBody></Table></CardContent>
  </Card>;
}
