---
sidebar_position: 8.6
---

# Gestoras

Uma **gestora** é um fundo da sala: o gestor investe o dinheiro dela e os cotistas compram **cotas**. O valor de uma cota é o **patrimônio por cota**: tudo o que a gestora tem (caixa, ações e renda fixa), menos o que ela deve, dividido pelo número de cotas.

Ex.: uma gestora com R$ 1.000.000 de patrimônio e 10.000 cotas tem patrimônio por cota de R$ 100,00.

## Emissão de novas cotas

Depois da oferta pública inicial, o gestor pode **emitir cotas novas** pelo botão **Emitir cotas** da página da gestora. Ele escolhe a quantidade, até o total de cotas que existem hoje, e a tela mostra antes de confirmar quanto entra no caixa e o que acontece com o controle.

- **Preço fixo:** as cotas novas custam o patrimônio por cota do dia do anúncio, e o preço não muda até o fim da emissão, mesmo que o patrimônio por cota ande.
- **Preferência (10 pregões):** só quem já tem cotas compra, até a proporção que tinha no anúncio. Ex.: com 20% das cotas numa emissão de 1.000, o direito é de 200 cotas. Comprar cotas no mercado depois do anúncio não dá direito.
- **Sobra (5 pregões):** o que ninguém comprou na preferência abre a todos, pelo livro de ofertas, ao mesmo preço fixo. Cada bot compra no máximo 20% da gestora.
- **O que não vende não nasce:** ao fim dos 15 pregões, as cotas que sobraram deixam de existir.
- **O dinheiro vai para o caixa da gestora**, menos a comissão dos Banqueiros de ofertas, se a sala tiver algum.

**Comissão dos Banqueiros de ofertas.** Cada oferta pública e cada emissão paga **1% do valor captado** aos jogadores com a profissão [Banqueiro de ofertas](lobby.md), em partes iguais, e o 1% sai do caixa da gestora: o comprador paga o mesmo. Ex.: uma captação de R$ 100.000,00 deixa R$ 99.000,00 na gestora e paga R$ 1.000,00 ao Banqueiro; com dois Banqueiros, cada um recebe R$ 500,00. Sem Banqueiro na sala, nada é descontado. O diálogo de emissão mostra a comissão antes de confirmar.

Quem não compra não perde: como o preço é o patrimônio por cota do dia, o patrimônio por cota de quem não comprou fica igual antes e depois da emissão. O que muda é a parte dele no total, que diminui. Por isso o gestor vê o aviso de controle: com menos de 50%, os outros cotistas podem juntar mais votos que ele numa assembleia.

## Emissão dirigida

Depois da oferta pública, o gestor principal também pode pôr **dinheiro novo** na gestora sem abrir a emissão para a sala, pelo botão **Emissão dirigida**. As cotas novas vão para **ele mesmo** ou para **um co-gestor ativo**, e o dinheiro sai do **caixa pessoal** de quem compra e entra no caixa da gestora.

- **Preço:** o maior entre o patrimônio por cota e o preço de ranking (o que o mercado paga pela cota hoje). Ex.: com patrimônio por cota de R$ 100,00 e ranking de R$ 120,00, a cota sai a R$ 120,00; com ranking de R$ 90,00, sai a R$ 100,00. Quem já tem cota não perde valor, porque ninguém entra abaixo do patrimônio por cota.
- **Teto:** o diálogo mostra o máximo de cotas antes de confirmar. Fora da partida de [aquisição hostil](./lobby.md#aquisição-hostil), uma emissão vai até o total de cotas que já existem (com 10.000 cotas, até 10.000 novas). Na aquisição hostil, o gestor principal e os co-gestores, somados, ficam com no máximo a fatia que a regra de mínimo de cotas no mercado permite, e o resto fica com o mercado. Ex.: com 35.740 cotas, 19.590 delas com os gestores e o mercado ficando com pelo menos 30%, o teto é de 18.093 cotas novas: depois delas, os gestores teriam 37.683 de 53.833 cotas, exatamente 70%.
- **Para onde vai o dinheiro:** primeiro quita a **taxa a pagar** que a gestora deve ao gestor, e o resto vai para o caixa. Ex.: R$ 110.440,00 numa gestora com R$ 18.420,00 de taxa a pagar: R$ 18.420,00 quitam a taxa e R$ 92.020,00 ficam no caixa.
- **Para si:** a compra liquida na hora, se o caixa pessoal cobrir o valor.
- **Para um co-gestor:** ele recebe uma **oferta** na página da gestora e em **Pendências**, válida por **7 dias**. Ao **aceitar**, o preço e o teto são os do dia do aceite, e o dinheiro sai do caixa pessoal dele naquele momento; ao **recusar** ou deixar vencer, nada acontece. O gestor pode **cancelar** a oferta enquanto ela espera, e só existe uma oferta por vez.

## Recompra

Pelo botão **Recomprar**, o gestor informa a **quantidade** de cotas e o **preço máximo** por cota. A gestora põe uma ordem de compra no livro, paga com o próprio caixa, e as cotas compradas **deixam de existir**.

- **Deságio** (preço abaixo do patrimônio por cota): o patrimônio por cota de quem ficou **sobe**. Ex.: a gestora com patrimônio por cota de R$ 100,00 recompra uma cota a R$ 90,00; o que sobrou do patrimônio se divide em menos cotas.
- **Ágio** (preço acima do patrimônio por cota): é permitido, e o diálogo mostra o **custo do ágio** em reais, o quanto a gestora paga acima do valor justo, antes de confirmar. Esse custo sai do patrimônio dos cotistas que ficam.
- Quem vende para a recompra recebe o preço da ordem. A gestora não compra cotas do próprio gestor: negócio entre contas do mesmo dono não existe.
- O gestor pode **cancelar o resto** da recompra; o que já foi comprado continua queimado.

A emissão e a recompra não acontecem ao mesmo tempo: enquanto uma está aberta, a outra espera.

## Troca de gestor pela assembleia

Quem tem **10% das cotas ou mais** pode **convocar uma assembleia** pelo botão **Convocar assembleia** da página da gestora. O convocador indica quem assume: ele mesmo ou um aliado jogador (bots não entram).

- **Convite:** se a indicação for um aliado, ele precisa **aceitar** em até 5 pregões. Recusa, silêncio ou cancelamento pelo convocador encerram o convite, e isso **não conta** no intervalo entre assembleias.
- **Votação (5 pregões):** abre no dia em que o convite é aceito, e o dia da abertura conta. Os votos são abertos, o placar aparece ao vivo e cada um pode mudar o voto até o fim.
- **Peso do voto:** as cotas que o votante tem no fechamento do 5º pregão. Ex.: quem tem 300 cotas e vota a favor soma 300 ao lado da troca.
- **Quem entra no placar:** o convocador já começa a favor. Só vota quem tem cota. O gestor não vota: as cotas dele contam **contra**. Quem não votou, os bots e o Mercado **abstêm**.
- **Resultado:** a troca acontece se as cotas a favor passam das cotas contra. **Empate mantém o gestor.**
- **Quem sai:** o gestor afastado vira cotista comum, perde a operação e as taxas futuras, e só pode fundar outra gestora depois de **6 meses**. A recompra aberta dele é cancelada.
- **Intervalo:** cada gestora tem no máximo **uma assembleia a cada 3 meses**, aberta ou concluída.

Do convite ao resultado a gestora **não emite cotas**. A **recompra segue liberada** e é a defesa do gestor: as cotas recompradas saem do total e do placar. Os cotistas recebem um aviso quando a votação abre e quando sai o resultado, e a assembleia vira manchete.

## Co-gestores

O gestor principal pode chamar até **3 co-gestores** pelo botão **Convidar co-gestor**, no cartão **Gestores** da página da gestora. O co-gestor **opera a carteira** (compra e vende ações e renda fixa em nome da gestora) e **divide as taxas** com o principal. Taxas, ofertas, emissões, recompras e a escolha de co-gestores seguem só com o principal. Bots não são convidados.

- **Parte nas taxas:** o principal escolhe quantos por cento das taxas de administração e de performance vão para cada co-gestor. Ex.: com a administração rendendo R$ 1.666,67 por mês e 20% para um co-gestor, ele recebe R$ 333,33 e o principal fica com R$ 1.333,34. A parte do principal é o que sobra, e ele sempre fica com pelo menos 1%.
- **Convite:** vale **7 dias** e já **reserva a parte** oferecida, então os convites pendentes contam na soma. O convidado responde pelo aviso da página ou pelas pendências. Ao aceitar, o acesso à carteira abre na hora.
- **Convite no lobby:** quem funda a gestora na aba **Gestora** da preparação também convida até **3 co-gestores** entre os jogadores da sala, e o convite já leva a **parte das taxas** (a soma deixa ao menos 1% ao principal, como na partida). O convidado aceita ou recusa na própria preparação; aceitar não impede de fundar a sua gestora nem de aceitar o convite de outra. Quem aceitou começa a partida como co-gestor ativo, com a parte valendo já nas taxas do **1º mês**; convite sem resposta quando a partida começa cai. Ex.: Ana funda a Aurora Gestão e convida o Caio com 20%; ele aceita no lobby e, no 1º dia, já opera a carteira da Aurora.
- **Quando a parte vale:** a parte nova, ou a parte mudada de quem já opera, entra nas taxas do **mês seguinte**. O cartão mostra a mudança agendada.
- **Saída:** o co-gestor pode **sair da gestão** e o principal pode **remover** um co-gestor. O acesso à carteira acaba no mesmo pregão, e a parte volta ao principal na próxima divisão de taxas.
- **Afastamento do principal:** se uma assembleia troca o gestor, o **co-gestor de maior parte** (no empate, o mais antigo) assume como principal e herda a parte de quem saiu. Sem co-gestor, a gestora fica congelada. Qualquer troca do gestor principal desliga a estratégia da carteira, e quem assume volta ao manual.
- **Presidência:** o gestor que vira presidente tem a gestora **em licença**. O co-gestor de maior parte assume enquanto durar o mandato e a gestora continua sendo do presidente: ele **não pode fundar outra**. Sem co-gestor, a carteira segue a **estratégia ligada** (veja **Automático da carteira**) e, sem estratégia, fica **congelada**: ela só volta a receber ordens quando o presidente liga uma estratégia ou convida um co-gestor, que assume na hora ao aceitar. No fim do mandato sem reeleição o automático desliga e o ex-presidente retoma a carteira. No fim do mandato sem reeleição, ou no impeachment, a gestora **volta** ao ex-presidente, desde que o gestor atual ainda seja quem assumiu na posse; o co-gestor que assumiu volta como co-gestor, com a parte que tinha antes, **se houver vaga**: com a lista cheia (3 co-gestores) ou sem parte sobrando ao principal (a soma das partes chegaria a 100%), ele não volta. Se uma assembleia trocou o gestor nesse meio-tempo, a gestora fica com quem assumiu e o ex-presidente pode fundar outra, no mesmo prazo. Na reeleição nada volta.

## Automático da carteira

O gestor principal, e os co-gestores ativos, podem pôr uma **estratégia** para operar a carteira da gestora: aba **Configurações**, cartão **Automático da carteira**. A lista é a mesma da página **Estratégias** e da aba **Minha preparação** do lobby, e cada gestora tem a estratégia dela, **independente da conta pessoal**: a estratégia da gestora opera só a carteira da gestora, e sua conta pessoal segue à mão.

- **Ligado:** as boletas da gestora travam e a estratégia opera a cada pregão. Na aba **Suas ações**, o cartão **O que o automático fez** mostra as últimas ordens, cada uma com o motivo.
- **Desligado:** a carteira volta ao manual. Trocar o gestor principal também desliga a estratégia.
- **Na presidência:** o automático solta só a **carteira**. Contribuição, oferta, taxas e convocação de assembleia seguem congeladas, e as taxas não correm até o fim do mandato. Desligar o automático congela a carteira até o fim do mandato.

## Fundar e gerir mais de uma

Só funda quem **não tem gestora**: quem já tem uma não funda outra, e a gestora em licença pela presidência conta como dele. Gerir mais de uma é normal no jogo: o co-gestor que assume a gestora de um presidente, ou que ganha uma em assembleia, passa a gerir as duas. Quem perde a gestora pode fundar outra, respeitando o prazo de 6 meses depois de afastado por assembleia.

**Operar pela gestora.** Ao escolher a gestora no caixa da barra de cima, a boleta de renda variável inteira troca para a cor da expansão Gestoras: a borda, o cabeçalho **Operando pela <gestora>** e o botão, que diz **Comprar** ou **Vender <ativo> pela gestora**. Comprar e vender usam a mesma cor; o lado da ordem se lê no seletor **Comprar | Vender** e no texto do botão. Quem é co-gestor vê o papel dele no cabeçalho. A faixa do alto e o seletor de conta seguem como estão, e a conta pessoal não muda.

## Ofertas públicas

O menu **Ofertas públicas**, logo depois de Gestoras, reúne as vendas de cotas novas a preço fixo e por tempo limitado. O número ao lado do nome é a quantidade de ofertas abertas agora. A página tem três blocos:

- **Sua preferência:** as emissões em que você já é cotista e ainda pode comprar antes dos outros, com a quantidade a que você tem direito, o custo, o prazo e quanto dos cotistas já comprou. Só aparece quando você tem direito a comprar.
- **Abertas a qualquer investidor:** a oferta pública inicial de uma gestora nova e a sobra de uma emissão, depois da preferência dos cotistas. Cada cartão mostra o preço fixo, quantas cotas ainda estão à venda, até quando vai e as taxas. Se o seu caixa compra menos do que resta, o cartão avisa quantas cotas ele alcança. Com uma gestora ativa, o cartão avisa que a compra sai da carteira pessoal e oferece voltar para ela.
- **Encerradas:** as ofertas que já fecharam, com o preço pago na oferta ao lado do preço da cota hoje no mercado e a diferença entre os dois. Ex.: uma oferta a R$ 100,00 com a cota hoje a R$ 101,80 aparece como "1,8% acima da oferta".

A compra sai pelo detalhe da cota, na renda variável: os botões **Comprar na oferta** e **Ver cota** levam até lá. Quando uma gestora abre oferta pública, o [Jornal](jornal.md) mostra a manchete numa janela central, com o botão **Comprar cotas**.

## A lista da sala

O menu **Gestoras** abre a lista da sala em três blocos: **Você gere** (as que você gere, as em licença e as de que você é co-gestor ativo), **Você tem cotas** e **Outras da sala**. Na linha da gestora que você opera aparecem os co-gestores, o selo "N para decidir" quando há convite, votação ou oferta esperando você, e o aviso de quando a gestora foi ganha em assembleia. O botão **Fundar minha gestora** fica no topo só para quem não tem gestora; ser co-gestor não conta como ter uma. Quem perdeu a gestora para a assembleia vê o aviso da troca e o botão **Fundar outra gestora**. A gestora em licença aparece no bloco **Você gere** com o aviso de que volta no fim do mandato.

