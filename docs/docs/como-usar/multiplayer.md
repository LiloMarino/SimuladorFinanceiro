---
sidebar_position: 3
---

# Multiplayer

O modo multiplayer permite que você compita com amigos em tempo real, testando suas estratégias de investimento sob as mesmas condições de mercado.

Todos os jogadores veem as mesmas movimentações e começam com o mesmo capital, garantindo uma competição justa.

---

## Como Funciona o Multiplayer

No modo multiplayer:

1. **Um jogador atua como Host (admin da simulação)**  
   Controla a sessão e inicia a simulação.

2. **Outros jogadores entram na sala**  
   Usando o IP ou link compartilhado.

3. **Todos começam com o mesmo capital**  
   Nenhum jogador tem vantagem inicial.

4. **A simulação acontece em tempo real**  
   As mesmas variações de mercado são aplicadas para todos.


:::warning Atenção
O host **não é automaticamente quem hospeda o servidor**  
e **não é escolhido automaticamente pelo sistema**.
:::

O host é um **papel lógico de administrador da simulação**, definido manualmente no `config.toml`.

Essa configuração é obrigatória:
- no multiplayer
- no singleplayer
- mesmo quando apenas uma pessoa está jogando

👉 Veja a explicação completa em [Lobby](/como-usar/lobby).

---

## Entrar com a Partida em Andamento

Quem chega depois do início não precisa esperar a próxima partida. Ao entrar com o nickname, uma tela mostra quem já joga, as cores que sobraram e o saldo inicial; basta escolher uma cor e clicar em **Entrar na partida**.

- **Saldo inicial na hora:** quem entra recebe o mesmo capital inicial dos outros, no dia em que a simulação está, e passa a aparecer no ranking e nas estatísticas.
- **Aporte mensal só dali em diante:** quem chega no dia 20 não recebe os aportes dos meses anteriores. O ranking por retorno continua comparável; o ranking por patrimônio absoluto reflete a data de chegada.
- **A vaga é de quem jogou, esteja online ou não:** a partida comporta até 10 jogadores. Quem saiu continua dono da vaga e da cor, então uma partida com 10 jogadores, seis deles offline, está cheia e ninguém novo entra.
- **Quem sai e volta mantém a cor** e o saldo da partida.

### Continuar uma partida salva

Ao selecionar uma partida salva, as cores de quem já jogou ficam reservadas, mesmo para quem não está na sala. Quem estava na sala e nunca jogou essa partida entra ao continuar, com o saldo inicial.

Se a partida salva não comporta a sala (jogadores da partida mais os novos passam de 10), o **Selecionar** fica desabilitado e o motivo aparece com os nomes. Com 10 jogadores salvos e um novato na sala, por exemplo, o novato precisa sair da sala ou o host escolhe outra partida; com 8 salvos e dois novatos, a partida carrega normalmente.

## Configuração de Rede

O multiplayer funciona através de **rede local (LAN)** ou **VPN**, dependendo de onde os jogadores estão conectados.



### Opção 1: Conexão via LAN (Mesma Rede Wi-Fi)

Se todos os jogadores estiverem na mesma rede local (ex: mesma casa ou escritório):

1. O host inicia a simulação e compartilha seu IP local  
   Exemplo: `192.168.1.100`
2. Os outros jogadores usam esse IP para se conectar
3. Todos acessam:  
   `http://<IP_DO_HOST>:8000`

:::tip
Esta é a opção mais simples e recomendada quando todos estão fisicamente próximos e conectados à mesma rede.
:::

---

### Opção 2: Conexão via VPN (Jogadores Remotos)

Para jogar com amigos que **não estão na mesma rede física**, é necessário usar uma **VPN**, criando uma rede virtual compartilhada entre os computadores.


#### Radmin VPN (Recomendado)

O **Radmin VPN** é gratuito, fácil de configurar e não possui limite de usuários.

**Instalação e uso:**

1. Baixe o Radmin VPN:  
   https://www.radmin-vpn.com/
2. Instale em todos os computadores que participarão
3. **O host cria uma rede:**
   - Abra o Radmin VPN
   - Clique em **Criar rede**
   - Defina um nome e uma senha
   - Compartilhe essas informações com os jogadores
4. **Os jogadores entram na rede:**
   - Clique em **Entrar em rede**
   - Informe o nome da rede e a senha
5. **Conexão:**
   - Todos verão o IP virtual do host na lista do Radmin VPN
   - Use esse IP para se conectar ao simulador

:::info
O Radmin VPN normalmente cria IPs no formato `26.x.x.x`.  
Este é o IP que deve ser usado para conexão.
:::


#### Outras Opções de VPN

- **Hamachi**  
  Gratuito para até 5 usuários. Indicado para grupos pequenos.

- **Tailscale**  
  Moderno, seguro e simples de configurar. Gratuito para uso pessoal.

---

## Configuração do `preferred_vpn`

O simulador tenta detectar automaticamente a VPN ativa e exibir o IP correto na tela do lobby do host.

Caso a detecção automática não funcione corretamente, é possível definir manualmente a VPN preferida no arquivo `config.toml`.

```toml
[server]
provider = "lan"
port = 8000
preferred_vpn = "radmin"
````

Define qual VPN o simulador deve priorizar ao exibir o IP de conexão.

---

## Link Copiável na Interface

Ao criar uma sala multiplayer, a interface exibe automaticamente um **link copiável** para facilitar o compartilhamento.

**Como usar:**

1. Crie a sala multiplayer
2. Clique no botão **Copiar Link**
3. O link completo será copiado
   Exemplo: `http://26.123.45.67:8000`
4. Compartilhe o link via Discord, WhatsApp ou qualquer outro meio
5. Os jogadores podem abrir o link diretamente no navegador para entrar na sala

---

## Túneis Públicos (Em Desenvolvimento)

Opções de túnel público como **LocalTunnel**, **Playit.gg** e **Zrok** estão em desenvolvimento.

Essas soluções permitirão compartilhar sessões multiplayer pela internet **sem a necessidade de VPN**, mas **ainda não estão disponíveis** nesta versão.

