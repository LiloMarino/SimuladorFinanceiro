import { useState, type ReactNode } from "react";
import { Line, LineChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Input } from "@/shared/components/ui/input";
import { Label } from "@/shared/components/ui/label";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/components/ui/tabs";
import { SortableTableHead } from "@/shared/components/sortable-table-head";
import { ErrorState } from "@/shared/components/error-state";
import { useTableSort } from "@/shared/hooks/useTableSort";
import { useSimulation } from "@/shared/hooks/useSimulation";
import type { SortValue } from "@/shared/lib/table-sort";
import { displayMoney, displayPercent } from "@/shared/lib/utils/display";
import type { GovernmentAction, GovernmentView } from "@/types";
import { useGovernment } from "../hooks/queries/useGovernment";
import { useGovernmentAction } from "../hooks/mutations/useGovernmentAction";
import { useGovernmentPreview } from "../hooks/mutations/useGovernmentPreview";

type Party = NonNullable<GovernmentView["state"]["parties"]>[number];
type Command = (action: GovernmentAction) => void;
const PRODUCTS = { STEEL: "Aço", OIL: "Petróleo e combustíveis", FOOD: "Alimentos", TECH: "Tecnologia" };
const POLICY_LABELS = {
  COMMON_TAX: "IR comum da renda variável", DAY_TRADE_TAX: "IR de day trade", FII_TAX: "IR dos FIIs",
  STOCK_EXEMPTION: "Limite de isenção de ações", FIXED_TAX_SHIFT: "Ajuste da tabela de renda fixa",
  LCI_TAX: "IR de LCI e LCA", SECTOR_TAX: "Ajuste por setor ou segmento", PRODUCT_TARIFF: "Tarifa de importação por produto", PUBLIC_SPENDING: "Investimento público",
};
const STATUS = { queued: "Na fila do Congresso", approved: "Aprovada", rejected: "Rejeitada", withdrawn: "Retirada" };
const dateLabel = (value: string | null | undefined) => value ? value.split("-").reverse().join("/") : "—";
const points = (value: number) => `${(value * 100).toLocaleString("pt-BR", { maximumFractionDigits: 2 })} p.p.`;
const person = (data: GovernmentView, id: number | null | undefined) => id == null ? "Sem indicação" : data.users[String(id)] ?? data.state.parties?.find(p=>p.candidate===id)?.candidate_name ?? ({ "-1": "Helena Prado", "-2": "Caio Alves", "-3": "Iara Lima", "-999": "Governo neutro" }[String(id)] ?? "Computador");
const partyColor = (party: Party) => party.is_ai ? "var(--muted-foreground)" : `var(--${party.color})`;

function Panel({ title, description, children }: { title: string; description?: string; children: ReactNode }) {
  return <Card><CardHeader><CardTitle>{title}</CardTitle>{description && <CardDescription>{description}</CardDescription>}</CardHeader><CardContent>{children}</CardContent></Card>;
}

function DataTable<T>({ rows, columns, rowKey }: {
  rows: T[]; rowKey: (row: T) => string | number;
  columns: { key: string; label: string; value: (row: T) => SortValue; cell: (row: T) => ReactNode; action?: boolean; numeric?: boolean }[];
}) {
  const sorting = useTableSort(rows, Object.fromEntries(columns.map(c => [c.key, c.value])));
  return <Table><TableHeader><TableRow>{columns.map(c => c.action ? <TableHead key={c.key}>{c.label}</TableHead> :
    <SortableTableHead key={c.key} label={c.label} numeric={c.numeric} {...sorting.header(c.key)} />)}</TableRow></TableHeader>
    <TableBody>{sorting.rows.map(row => <TableRow key={rowKey(row)}>{columns.map(c => <TableCell key={c.key} numeric={c.numeric}>{c.cell(row)}</TableCell>)}</TableRow>)}
      {rows.length === 0 && <TableRow><TableCell colSpan={columns.length}>Ainda não há registros.</TableCell></TableRow>}
    </TableBody></Table>;
}

export default function GovernmentPage({ initialTab = "government" }: { initialTab?: string }) {
  const query = useGovernment();
  const { simulation } = useSimulation();
  if (!simulation?.simulation?.government?.enabled) return <Panel title="Expansão Governo" description="O host pode ativar esta expansão nas regras de uma nova partida com ao menos 5 anos."><p>A carreira política é opcional. Todos continuam podendo investir quando a expansão está desligada.</p></Panel>;
  if (query.error) return <ErrorState title="Não deu para carregar o governo" description="A partida continua. Tente novamente." error={query.error} onRetry={() => void query.refetch()} />;
  if (!query.data) return <Skeleton className="h-80 w-full" />;
  return <GovernmentContent data={query.data} initialTab={initialTab} />;
}

function GovernmentContent({ data, initialTab }: { data: GovernmentView; initialTab: string }) {
  const mutation = useGovernmentAction();
  const send: Command = action => mutation.mutate(action);
  const { state } = data;
  const term = state.term;
  return <div className="grid gap-5">
    <div><h1 className="text-2xl font-semibold">Governo e política</h1><p className="text-sm text-muted-foreground">{dateLabel(data.today)} · {term ? `Presidência: ${person(data, term.president)}` : "Governo do computador até a primeira posse"} · Participação política opcional</p></div>
    <Tabs key={initialTab} defaultValue={initialTab}>
      <TabsList><TabsTrigger value="election">Eleição</TabsTrigger><TabsTrigger value="government">Governo</TabsTrigger><TabsTrigger value="impacts">Impactos e modelo</TabsTrigger></TabsList>
      <TabsContent value="election"><div className="grid gap-5"><Election data={data} /><PartyManagement data={data} send={send} pending={mutation.isPending} /><Rankings data={data} /></div></TabsContent>
      <TabsContent value="government"><div className="grid gap-5"><GovernmentPanel data={data} send={send} pending={mutation.isPending} /><PolicyForm data={data} send={send} pending={mutation.isPending} /><PublicLog data={data} /></div></TabsContent>
      <TabsContent value="impacts"><ImpactPanel data={data} /></TabsContent>
    </Tabs>
  </div>;
}

function Election({ data }: { data: GovernmentView }) {
  const { state, election_year: year } = data;
  const latest = state.poll_history?.at(-1);
  const result = state.results?.at(-1);
  return <>
    <Panel title={`Eleição de outubro de ${year}`} description="Mandato de 4 anos, uma reeleição. O computador completa as vagas até três chapas. Pesquisas expressam votos válidos do eleitorado simulado.">
      <div className="grid gap-3 text-sm md:grid-cols-4">{[
        ["Campanha", `07/10/${year - 1} até 06/10/${year}`], ["Primeiro turno", `07/10/${year}`], ["Segundo turno, se necessário", `28/10/${year}`], ["Posse", `01/01/${year + 1}`],
      ].map(([label, value]) => <div key={label} className="rounded-md border p-3"><b>{label}</b><p>{value}</p></div>)}</div>
      <p className="mt-3 text-sm">{data.phase === "campaign" ? "Inscrições e campanha abertas." : data.phase === "runoff" ? "Segundo turno: partidos eliminados e não filiados podem doar a um finalista." : "Fora da campanha: partidos continuam disponíveis; a próxima inscrição abre no calendário acima."}</p>
    </Panel>
    <Panel title="Pesquisa de intenção de voto" description="Alcance depende da campanha com retorno decrescente; programa e aprovação pesam de forma diferente em cada perfil.">
      <div className="h-64"><ResponsiveContainer width="100%" height="100%"><LineChart data={state.poll_history ?? []}><CartesianGrid stroke="var(--border)" /><XAxis dataKey="on" tickFormatter={s => dateLabel(String(s)).slice(3)} /><YAxis unit="%" /><Tooltip />{(state.parties ?? []).map(p => <Line key={p.id} dataKey={String(p.id)} name={p.acronym} stroke={partyColor(p)} strokeDasharray={p.is_ai ? "5 4" : undefined} dot={false} isAnimationActive={false} connectNulls />)}</LineChart></ResponsiveContainer></div>
      <DataTable rows={(state.parties ?? []).filter(p=>!p.is_ai || p.campaign_active)} rowKey={p => p.id} columns={[
        { key: "party", label: "Partido e chapa", value: p => p.acronym, cell: p => <span className="grid"><b style={{ color: partyColor(p) }}>{p.acronym} · {p.name}</b><span>{person(data, p.candidate)}{p.is_ai ? " · computador" : ` · vice: ${p.vice_accepted ? person(data, p.vice) : p.vice ? "convite pendente" : "sem vice"}`}</span></span> },
        { key: "members", label: "Filiados", value: p => p.members?.length ?? 0, cell: p => p.is_ai ? "Computador" : p.members?.map(id => person(data, id)).join(", ") },
        { key: "votes", label: "Última pesquisa", value: p => latest?.[String(p.id)] == null ? null : Number(latest[String(p.id)]), cell: p => latest?.[String(p.id)] == null ? "Sem pesquisa" : `${Number(latest[String(p.id)]).toFixed(1)}%`, numeric: true },
        { key: "budget", label: "Contribuição/mês", value: p => Object.values(p.contributions ?? {}).reduce((a,b) => a + Number(b),0), cell: p => p.is_ai ? `${state.rules.difficulty === "easy" ? "0,5" : state.rules.difficulty === "hard" ? "1,5" : "1"}× a média` : displayMoney(Object.values(p.contributions ?? {}).reduce((a,b) => a + Number(b),0)), numeric: true },
        { key: "spent", label: "Gasto na campanha", value: p => Number(p.spent), cell: p => displayMoney(p.spent), numeric: true },
        { key: "promise", label: "Promessa · 1 a 5", value: p => p.promise, cell: p => p.promise, numeric: true },
      ]} />
      <p className="mt-3 text-xs text-muted-foreground">1: cortar impostos · 2: isenção setorial · 3: equilíbrio · 4: taxar setor · 5: imposto geral/gasto alto. Vence no primeiro turno quem superar 50% dos votos válidos; empates têm desempate reproduzível pela semente.</p>
    </Panel>
    {result && <Panel title={`Resultado · ${result.round}º turno de ${result.year}`} description={`Apuração em ${dateLabel(result.on)}. ${result.winner == null ? result.round === 2 ? "Sem candidaturas válidas; governo neutro assume na posse." : "Haverá segundo turno." : "Eleição encerrada; o mandato começa na posse."}`}>
      <DataTable rows={Object.entries(result.votes).map(([id,votes]) => ({ id, votes }))} rowKey={r => r.id} columns={[
        {key:"party",label:"Partido",value:r=>(state.parties ?? []).find(p=>String(p.id)===r.id)?.acronym,cell:r=>(state.parties ?? []).find(p=>String(p.id)===r.id)?.name ?? r.id},
        {key:"votes",label:"Votos válidos",value:r=>r.votes,cell:r=>`${r.votes.toFixed(2)}%`,numeric:true},
      ]} />
      <div className="mt-3 grid gap-2 text-sm">{Object.entries(result.by_profile ?? {}).map(([profile,votes]) => <p key={profile}><b>{profile}:</b> {Object.entries(votes).map(([id,v])=>`${(state.parties ?? []).find(p=>String(p.id)===id)?.acronym ?? id}: ${v.toFixed(1)}%`).join(" · ")}</p>)}</div>
    </Panel>}
  </>;
}

function PartyManagement({ data, send, pending }: {data:GovernmentView;send:Command;pending:boolean}) {
  const own = (data.state.parties ?? []).find(p=>p.members?.includes(data.my_id));
  const [name,setName] = useState(""); const [acronym,setAcronym] = useState("");
  const [color,setColor] = useState(() => Array.from({length:10},(_,i)=>`chart-${i+1}`).find(c=>!(data.state.parties ?? []).some(p=>p.color===c)) ?? "chart-1"); const [promise,setPromise] = useState(3);
  const [amount,setAmount] = useState("0"); const [candidate,setCandidate] = useState(String(data.my_id)); const [vice,setVice] = useState("");
  const options = (data.state.parties ?? []).filter(p=>!p.is_ai && p.founder != null);
  return <Panel title={own ? `Seu partido · ${own.acronym}` : "Participar da política"} description="Filiação é voluntária. Só uma indicação aceita pessoalmente coloca o jogador na disputa. Contribuições e doações saem do caixa e reduzem o patrimônio e o retorno financeiro.">
    <div className="grid gap-4">
      <Label className="grid">Sua contribuição mensal (R$; pode ser zero)<Input type="number" min="0" step="100" value={amount} onChange={e=>setAmount(e.target.value)} /></Label>
      {!own ? <>
        <form className="grid gap-3 sm:grid-cols-2" onSubmit={e=>{e.preventDefault();send({action:"found",name,acronym,color,promise,amount});}}>
          <Label className="grid">Nome do partido<Input required minLength={3} maxLength={70} value={name} onChange={e=>setName(e.target.value)} /></Label>
          <Label className="grid">Sigla (2 a 5 letras)<Input required minLength={2} maxLength={5} value={acronym} onChange={e=>setAcronym(e.target.value.toUpperCase())} /></Label>
          <Label className="grid">Cor<select className="h-9 rounded-md border bg-background px-3" value={color} onChange={e=>setColor(e.target.value)}>{Array.from({length:10},(_,i)=>`chart-${i+1}`).map(c=><option key={c} disabled={(data.state.parties ?? []).some(p=>p.color===c)} value={c}>Cor {c.split("-")[1]}</option>)}</select></Label>
          <Label className="grid">Programa · faixa {promise}<Input type="range" min="1" max="5" step="0.5" value={promise} onChange={e=>setPromise(Number(e.target.value))} /></Label>
          <Button disabled={pending} type="submit">Fundar partido</Button>
        </form>
        <div className="flex flex-wrap gap-2">{options.map(p=><Button key={p.id} disabled={pending} variant="outline" onClick={()=>send({action:"join",party_id:p.id,amount})}>Filiar-se ao {p.acronym}</Button>)}</div>
        <p className="text-xs text-muted-foreground">Continuar sem partido mantém o fluxo normal de investimento.</p>
      </> : <>
        <div className="flex gap-2"><Button disabled={pending} onClick={()=>send({action:"contribute",amount})}>Alterar contribuição</Button><Button disabled={pending} variant="outline" onClick={()=>send({action:"leave"})}>Sair do partido</Button></div>
        <DataTable rows={own.members ?? []} rowKey={id=>id} columns={[
          {key:"name",label:"Filiado",value:id=>person(data,id),cell:id=>person(data,id)},
          {key:"contribution",label:"Contribuição mensal",value:id=>Number(own.contributions?.[String(id)]??0),cell:id=>displayMoney(own.contributions?.[String(id)]??"0"),numeric:true},
          {key:"role",label:"Função",value:id=>id===own.founder?"Fundador":id===own.candidate?"Candidato":id===own.vice?"Vice":"Filiado",cell:id=>id===own.founder?"Fundador":id===own.candidate?"Candidato":id===own.vice?"Vice":"Filiado"},
          {key:"action",label:"Ações",value:id=>id,action:true,cell:id=>own.founder===data.my_id && id!==data.my_id?<Button size="sm" variant="outline" disabled={pending} onClick={()=>send({action:"expel",party_id:own.id,member_id:id})}>Expulsar</Button>:null},
        ]} />
        {own.founder===data.my_id && <form className="flex flex-wrap items-end gap-3" onSubmit={e=>{e.preventDefault();send({action:"nominate",member_id:Number(candidate),vice_id:vice?Number(vice):null});}}>
          <Label className="grid">Candidato<select className="h-9 rounded-md border bg-background px-3" value={candidate} onChange={e=>setCandidate(e.target.value)}>{own.members?.map(id=><option key={id} value={id}>{person(data,id)}</option>)}</select></Label>
          <Label className="grid">Convidar vice<select className="h-9 rounded-md border bg-background px-3" value={vice} onChange={e=>setVice(e.target.value)}><option value="">Sem vice</option>{own.members?.filter(id=>String(id)!==candidate).map(id=><option key={id} value={id}>{person(data,id)}</option>)}</select></Label>
          <Button type="submit" disabled={pending || data.phase!=="campaign"}>Inscrever chapa / convidar</Button>
        </form>}
        {own.candidate===data.my_id && !own.candidate_accepted && <div className="flex gap-2"><Button disabled={pending} onClick={()=>send({action:"accept_candidate"})}>Aceitar candidatura</Button><Button variant="outline" disabled={pending} onClick={()=>send({action:"decline_candidate"})}>Recusar candidatura</Button></div>}
        {own.vice===data.my_id && !own.vice_accepted && <div className="flex gap-2"><Button disabled={pending} onClick={()=>send({action:"accept_vice"})}>Aceitar convite para vice</Button><Button variant="outline" disabled={pending} onClick={()=>send({action:"decline_vice"})}>Recusar convite</Button></div>}
      </>}
      {data.phase==="runoff" && (!own || !data.state.finalists?.includes(own.id)) && <div className="grid gap-2"><p>Doação avulsa entre os turnos (valor do campo acima):</p><div className="flex gap-2">{data.state.finalists?.map(id=><Button key={id} disabled={pending || Number(amount)<=0} onClick={()=>send({action:"donate",party_id:id,amount})}>Doar {displayMoney(amount||0)} ao {(data.state.parties ?? []).find(p=>p.id===id)?.acronym}</Button>)}</div></div>}
    </div>
  </Panel>;
}

function Rankings({data}:{data:GovernmentView}) {
  return <Panel title="Ranking de partidos" description={data.state.rules.ranking==="parties"?"A soma dos patrimônios dos filiados decide a partida. Partidos do computador ficam fora.":"Comparação pública; o ranking individual continua decidindo a partida."}>
    <DataTable rows={data.party_ranking} rowKey={p=>p.party_id} columns={[
      {key:"name",label:"Partido",value:p=>p.name,cell:p=>p.name},
      {key:"members",label:"Filiados",value:p=>p.members.join(", "),cell:p=>p.members.join(", ")},
      {key:"wealth",label:"Patrimônio somado",value:p=>Number(p.networth),cell:p=>displayMoney(p.networth),numeric:true},
    ]} />
  </Panel>;
}

function GovernmentPanel({data,send,pending}:{data:GovernmentView;send:Command;pending:boolean}) {
  const [selic,setSelic] = useState(() => (data.current_selic * 100).toFixed(2));
  const term=data.state.term;
  return <>
    <Panel title={term?`Presidência · ${person(data,term.president)}`:"Antes da primeira posse"} description={term?`Mandato: ${dateLabel(term.start)} a ${dateLabel(term.end)}. ${term.neutral?"Governo neutro: sem novas medidas.":"Fila pública; apenas o presidente propõe e retira medidas."}`:"A primeira eleição define o presidente; ser host não concede poderes de governo."}>
      <div className="grid gap-4 sm:grid-cols-3"><div><p>Aprovação</p><b className="font-mono text-2xl">{term?`${term.approval?.toFixed(1)}%`:"—"}</b></div><div><p>Orçamento livre</p><b>{displayMoney(Number(data.state.treasury)-Number(data.state.reserved_spending))}</b><p className="text-xs">Reservado: {displayMoney(data.state.reserved_spending)}</p></div><div><p>Impeachment</p><b>{term?.low_months ?? 0} / {data.state.rules.impeachment_months ?? 3} meses abaixo de {data.state.rules.impeachment_floor ?? 25}%</b></div></div>
      <div className="mt-4 flex flex-wrap gap-2">{Object.entries(data.approval_factors).map(([key,v])=><Badge key={key} variant="secondary">{key}: {v>0?"+":""}{v.toFixed(1)}</Badge>)}</div>
      <p className="mt-2 text-xs text-muted-foreground">Fatores estimados para o próximo fechamento. A aprovação vigente é atualizada mensalmente.</p>
      <p className="mt-3 text-xs text-muted-foreground">Base 50 na posse. Inflação na meta +4; cada ponto acima −3. Bolsa: ±1 por 5% em 12 meses, até ±6. Impostos e cortes perdem força em 6 meses; promessa: −3 por faixa de distância.</p>
      <div className="mt-4 h-44"><ResponsiveContainer width="100%" height="100%"><LineChart data={data.state.approval_history ?? []}><XAxis dataKey="on" /><YAxis domain={[0,100]} /><Tooltip /><Line type="monotone" dataKey="approval" name="Aprovação (%)" stroke="var(--primary)" dot={false} isAnimationActive={false} /></LineChart></ResponsiveContainer></div>
    </Panel>
    <Panel title="Regras tributárias em vigor" description="IR altera o imposto sobre os ganhos; tarifas de produtos também podem mudar a cotação pelo modelo empresarial. Ajustes de setor e segmento são somados ao IR, com limite de 0% a 50%.">
      <DataTable rows={data.current_taxes} rowKey={r=>r.label} columns={[
        {key:"name",label:"Regra",value:r=>r.label,cell:r=>r.label},
        {key:"value",label:"Hoje",value:r=>Number(r.value),cell:r=>r.unit==="money"?displayMoney(r.value):displayPercent(r.value),numeric:true},
      ]} />
    </Panel>
    <Panel title="Congresso e medidas" description="Proposta pública → votação no fechamento do mês → 90 dias → vigência. A chance de aprovação é a aprovação do governo no momento do voto; rejeições podem ser reapresentadas.">
      <DataTable rows={data.state.policies ?? []} rowKey={p=>p.id} columns={[
        {key:"kind",label:"Medida",value:p=>POLICY_LABELS[p.kind],cell:p=><span className="grid"><b>{POLICY_LABELS[p.kind]}</b><span>{PRODUCTS[p.target as keyof typeof PRODUCTS] ?? p.target}</span></span>},
        {key:"value",label:"Valor",value:p=>Number(p.value),cell:p=>["PUBLIC_SPENDING","STOCK_EXEMPTION"].includes(p.kind)?displayMoney(p.value):displayPercent(p.value),numeric:true},
        {key:"proposed",label:"Proposta",value:p=>p.proposed_on,cell:p=>dateLabel(p.proposed_on)},
        {key:"status",label:"Situação",value:p=>STATUS[p.status??"queued"],cell:p=>STATUS[p.status??"queued"]},
        {key:"effective",label:"Vigência",value:p=>p.effective_on,cell:p=>p.effective_on&&p.effective_on>data.today?`A caminho · ${dateLabel(p.effective_on)}`:dateLabel(p.effective_on)},
        {key:"action",label:"Ações",action:true,value:p=>p.id,cell:p=>data.can_govern&&p.status==="queued"?<Button size="sm" variant="outline" disabled={pending} onClick={()=>send({action:"withdraw",policy_id:p.id})}>Retirar</Button>:null},
      ]} />
    </Panel>
    <Panel title="Política monetária" description={data.state.rules.manual_selic?`Decisões com intervalo de 45 dias. Próxima oportunidade: ${dateLabel(data.next_selic_meeting)}.`:"Banco Central autônomo: responde ao IPCA adicional com 1,5 vez a variação. A regra foi fixada no lobby."}>
      <p className="text-sm">Taxas atuais: inflação {displayPercent(data.current_inflation)} · SELIC {displayPercent(data.current_selic)} a.a.</p>
      <p className="mt-2 text-sm">Efeito atual nas taxas anuais: IPCA {points(data.inflation_delta)} · SELIC {points(data.selic_delta)}.</p>
      {data.state.rules.manual_selic&&data.can_govern&&<form className="mt-3 flex items-end gap-2" onSubmit={e=>{e.preventDefault();send({action:"selic",value:String(Number(selic)/100)});}}><Label className="grid">Nova SELIC (% a.a.)<Input type="number" min="0" max="100" step="0.01" value={selic} onChange={e=>setSelic(e.target.value)} /></Label><Button disabled={pending} type="submit">Publicar decisão</Button></form>}
      <p className="mt-2 text-xs text-muted-foreground">Limite por decisão: 0,75 ponto em inflação normal; 1,5 quando a inflação supera a meta em 2 pontos; 3 quando supera em 10 pontos. Abaixo da referência, a inflação reage após 90 dias. Taxas e cotações usam o mesmo modelo da carteira.</p>
    </Panel>
    <Panel title="Carteira pública do presidente" description="A carteira fica congelada no mandato; vencimentos e rendimentos seguem automáticos.">
      {data.president_finances && <p className="mb-3 text-sm">Patrimônio: {displayMoney(data.president_finances.total_networth)} · Caixa: {displayMoney(data.president_finances.cash)} · Renda fixa: {displayMoney(data.president_finances.fixed_income_value)}</p>}
      <div className="flex flex-wrap gap-2">{Object.entries(data.president_portfolio).map(([ticker,size])=><Badge key={ticker} variant="secondary">{ticker}: {size}</Badge>)}{Object.keys(data.president_portfolio).length===0&&<p>Sem posições em ações, ou presidência do computador.</p>}</div>
      {!!data.president_finances?.fixed_income.length && <DataTable rows={data.president_finances.fixed_income} rowKey={p=>String(p.asset.asset_uuid)} columns={[
        {key:"title",label:"Título",value:p=>p.asset.investment_type,cell:p=>`${p.asset.investment_type} · ${p.asset.rate_index}`},
        {key:"applied",label:"Aplicado",value:p=>Number(p.total_applied),cell:p=>displayMoney(p.total_applied),numeric:true},
        {key:"value",label:"Valor atual",value:p=>Number(p.current_value),cell:p=>displayMoney(p.current_value),numeric:true},
        {key:"maturity",label:"Vencimento",value:p=>p.asset.maturity_date,cell:p=>dateLabel(p.asset.maturity_date)},
      ]} />}
    </Panel>
  </>;
}

function PolicyForm({data,send,pending}:{data:GovernmentView;send:Command;pending:boolean}) {
  const preview = useGovernmentPreview();
  const [kind,setKind]=useState<GovernmentAction["kind"]>("COMMON_TAX");
  const [value,setValue]=useState("15"); const [target,setTarget]=useState("");
  const money=kind==="PUBLIC_SPENDING"||kind==="STOCK_EXEMPTION";
  const previewMatches = preview.variables?.kind === kind && preview.variables?.target === target && preview.variables?.value === (money ? value : String(Number(value)/100));
  const sectors=[...new Set(data.state.rules.companies?.flatMap(c=>[c.sector,c.segment]).filter((s):s is string=>!!s)??[])].sort();
  return <Panel title="Nova medida" description="O presidente propõe dentro do catálogo da partida. O Congresso decide; a proposta não altera preços nem cobra imposto antes da vigência.">
    <p className="mb-3 text-sm">{data.can_govern ? "Simule os efeitos antes de publicar." : "A prévia é pública para toda a sala; apenas o presidente pode publicar uma proposta."}</p>
    <form className="grid gap-3 sm:grid-cols-2" onSubmit={e=>{e.preventDefault();send({action:"propose",kind,target,value:money?value:String(Number(value)/100)});}}>
      <Label className="grid">Instrumento<select className="h-9 rounded-md border bg-background px-3" value={kind} onChange={e=>{setKind(e.target.value as GovernmentAction["kind"]);setTarget("");setValue(e.target.value==="PUBLIC_SPENDING"?"10000000":e.target.value==="STOCK_EXEMPTION"?"20000":e.target.value==="PRODUCT_TARIFF"?"10":"0");}}>{Object.entries(POLICY_LABELS).map(([key,label])=><option key={key} value={key}>{label}</option>)}</select></Label>
      <Label className="grid">{money?"Valor (R$)":kind==="SECTOR_TAX"||kind==="FIXED_TAX_SHIFT"?"Ajuste em pontos percentuais":"Alíquota (%)"}<Input required type="number" step={money?"1000":"0.25"} value={value} onChange={e=>setValue(e.target.value)} /></Label>
      {(kind==="SECTOR_TAX"||kind==="PRODUCT_TARIFF")&&<Label className="grid">Alvo<select required className="h-9 rounded-md border bg-background px-3" value={target} onChange={e=>setTarget(e.target.value)}><option value="">Escolha</option>{(kind==="PRODUCT_TARIFF"?Object.entries(PRODUCTS):sectors.map(s=>[s,s])).map(([key,label])=><option key={key} value={key}>{label}</option>)}</select></Label>}
      <p className="self-center text-xs text-muted-foreground">Gasto público: R$ 1 a 100 milhões por programa, dentro do orçamento livre; inflação começa após 30 dias de execução e perde metade da força por ano. A aprovação só permite execução após 90 dias.</p>
      <Button type="button" variant="outline" disabled={preview.isPending} onClick={()=>preview.mutate({action:"propose",kind,target,value:money?value:String(Number(value)/100)})}>Simular medida</Button>
      <Button type="submit" disabled={pending || !data.can_govern}>Publicar proposta no Congresso</Button>
    </form>
    {preview.data && previewMatches && <div className="mt-4 grid gap-3"><p className="text-sm">Referência de {dateLabel(preview.data.as_of)}. {preview.data.assumptions} Vigência mais cedo: {dateLabel(preview.data.earliest_effective_on)}. Efeito inflacionário estimado: {displayPercent(preview.data.inflation_delta)}.</p><DataTable rows={preview.data.impacts} rowKey={p=>p.ticker} columns={[
      {key:"ticker",label:"Ativo",value:p=>p.ticker,cell:p=>p.ticker},
      {key:"coverage",label:"Perfil",value:p=>p.covered?1:0,cell:p=>p.covered?"Hipótese coberta":"Cobertura insuficiente para produtos"},
      {key:"base",label:"Referência de hoje",value:p=>p.baseline_price,cell:p=>displayMoney(p.baseline_price),numeric:true},
      {key:"effect",label:"Com a medida simulada",value:p=>p.effective_price,cell:p=>displayMoney(p.effective_price),numeric:true},
      {key:"impact",label:"Efeito total do governo",value:p=>p.impact,cell:p=>displayPercent(p.impact),numeric:true},
    ]} /></div>}
  </Panel>;
}

function ImpactPanel({data}:{data:GovernmentView}) {
  return <div className="grid gap-5">
    <Panel title="Produto → empresa → ação" description="Contrafactual do modelo: mesma série e mesmas ordens, mudando apenas o efeito governamental. Os perfis são hipóteses do cenário; não representam previsões da bolsa real.">
      <DataTable rows={data.impacts} rowKey={p=>p.ticker} columns={[
        {key:"ticker",label:"Ativo",value:p=>p.ticker,cell:p=><span className="grid"><b>{p.ticker}</b><span>{p.sector??"Sem setor"}</span></span>},
        {key:"covered",label:"Perfil de produtos",value:p=>p.covered?1:0,cell:p=>p.covered?p.exposures.map(e=>`${PRODUCTS[e.product]}: receita ${(e.revenue_share*100).toFixed(0)}%, custo importado ${(e.imported_cost_share*100).toFixed(0)}%`).join(" · "):"Cobertura insuficiente para produtos"},
        {key:"baseline",label:"Sem governo",value:p=>p.baseline_price,cell:p=>displayMoney(p.baseline_price),numeric:true},
        {key:"effective",label:"Com governo",value:p=>p.effective_price,cell:p=>displayMoney(p.effective_price),numeric:true},
        {key:"product",label:"Canal empresarial",value:p=>p.product_effect,cell:p=>displayPercent(p.product_effect),numeric:true},
        {key:"monetary",label:"Canal monetário",value:p=>p.monetary_effect,cell:p=>displayPercent(p.monetary_effect),numeric:true},
        {key:"impact",label:"Efeito total",value:p=>p.impact,cell:p=>displayPercent(p.impact),numeric:true},
      ]} />
      <p className="mt-3 text-xs text-muted-foreground">A tarifa encarece insumos importados e pode beneficiar produtores locais. O repasse reduz a pressão de custos. O lucro operacional é dividido pela margem; 20% dessa variação entra na avaliação da ação. SELIC: −2,9% por ponto adicional, vezes o beta. O efeito permanente é aplicado uma vez sobre a referência diária; medidas do mesmo tipo e alvo se substituem.</p>
    </Panel>
    <Panel title="Perfis de eleitores" description="Pesos e preferências são regras fictícias da partida; não representam pesquisa eleitoral real."><DataTable rows={data.state.rules.electorate??[]} rowKey={g=>g.name} columns={[
      {key:"name",label:"Perfil",value:g=>g.name,cell:g=>g.name}, {key:"weight",label:"Peso",value:g=>g.weight,cell:g=>displayPercent(g.weight),numeric:true},
      {key:"position",label:"Posição na régua",value:g=>g.position,cell:g=>g.position,numeric:true}, {key:"campaign",label:"Sensibilidade à campanha",value:g=>g.campaign_sensitivity,cell:g=>g.campaign_sensitivity,numeric:true},
    ]} /></Panel>
    <Panel title="Regras econômicas desta partida" description={data.state.rules.model_version}>
      <p className="text-sm">Orçamento público inicial: {displayMoney(data.state.rules.initial_treasury??0)}. Cada R$ 100 milhões de investimento adiciona {points(data.state.rules.spending_inflation??0.01)} à inflação anual, após 30 dias, com meia-vida de 365 dias. A resposta inflacionária à diferença de SELIC usa coeficiente {data.state.rules.monetary_inflation??0.25} e atraso de 90 dias. Parâmetros ficam gravados na partida.</p>
      <p className="mt-2 text-xs text-muted-foreground">As séries comuns são preservadas. Efeitos da vigência permanecem até substituição; gasto público decai. Limites de preço e taxa mantêm os resultados numéricos válidos. Anúncios são públicos e não aplicam um segundo choque financeiro.</p>
    </Panel>
  </div>;
}

function PublicLog({data}:{data:GovernmentView}) {
  return <Panel title="Linha do tempo pública" description="Filiações, contribuições, doações, eleições, posse e decisões."><DataTable rows={(data.state.log??[]).map((r,index)=>({on:r.on,text:r.text,index}))} rowKey={r=>r.index} columns={[
    {key:"date",label:"Data",value:r=>r.on,cell:r=>dateLabel(r.on)}, {key:"event",label:"Evento",value:r=>r.text,cell:r=><span className="whitespace-normal">{r.text}</span>},
  ]} /></Panel>;
}
