---
sidebar_position: 1
---

# Multiplayer

O modo multiplayer permite que você compita com amigos em tempo real, testando suas estratégias de investimento uns contra os outros.

## Como Funciona o Multiplayer

No modo multiplayer:

1. **Um jogador cria a sala (Host)** - Define as configurações iniciais da simulação
2. **Outros jogadores entram na sala** - Usando o IP/link compartilhado pelo host
3. **Todos começam com o mesmo capital** - Condições iguais para competição justa
4. **Simulação acontece em tempo real** - Todos veem as mesmas movimentações de mercado
5. **Vencedor é quem tem maior patrimônio** - Ao final do período da simulação

## Configuração de Rede

O multiplayer funciona através de **conexão de rede local (LAN)** ou **VPN**.

### Opção 1: Conexão via LAN (Mesma Rede Wi-Fi)

Se todos os jogadores estiverem na mesma rede Wi-Fi:

1. O host inicia a simulação e compartilha seu IP local (ex: `192.168.1.100`)
2. Os outros jogadores usam este IP para se conectar
3. Todos acessam `http://<IP_DO_HOST>:8000`

:::tip
Esta é a opção mais simples se todos estiverem fisicamente próximos e conectados à mesma rede.
:::

### Opção 2: Conexão via VPN (Jogadores Remotos)

Para jogar com amigos que não estão na mesma rede física, use uma **VPN** para criar uma rede virtual.

#### Radmin VPN (Recomendado)

**Radmin VPN** é gratuito, fácil de usar e não tem limite de usuários.

**Instalação:**

1. Baixe o Radmin VPN: [radmin-vpn.com](https://www.radmin-vpn.com/)
2. Instale em todos os computadores que participarão
3. **Host cria uma rede:**
   - Abra o Radmin VPN
   - Clique em "Criar rede"
   - Defina um nome e senha
   - Compartilhe estas informações com os jogadores
4. **Jogadores entram na rede:**
   - Abra o Radmin VPN
   - Clique em "Entrar em rede"
   - Digite o nome da rede e senha fornecidos pelo host
5. **Conectar:**
   - Todos os jogadores verão o IP virtual do host na lista do Radmin VPN
   - Use este IP para se conectar ao simulador

:::info
O Radmin VPN cria IPs virtuais que começam geralmente com `26.x.x.x`. Use este IP para conexão.
:::

#### Outras Opções de VPN

- **Hamachi** - Gratuito para até 5 usuários. Boa para grupos pequenos.
- **Tailscale** - Moderno, seguro e fácil de configurar. Gratuito para uso pessoal.
- **ZeroTier** - Open-source e gratuito.

### Configuração do preferred_vpn

O simulador pode detectar automaticamente sua VPN e usar o IP correto.

Edite o arquivo `config.toml` na raiz do projeto:

```toml
[server]
provider = "lan"
port = 8000
preferred_vpn = "radmin"  # ou "hamachi", "tailscale", "zerotier"
```

Opções disponíveis:
- `"radmin"` - Radmin VPN
- `"hamachi"` - LogMeIn Hamachi
- `"tailscale"` - Tailscale VPN
- `"zerotier"` - ZeroTier VPN
- `null` - Detectar automaticamente

:::tip
Se você configurar o `preferred_vpn`, o simulador mostrará automaticamente o IP correto da VPN na interface, facilitando o compartilhamento com outros jogadores.
:::

## Link Copiável na Interface

Quando você cria uma sala no modo multiplayer, a interface mostra um **link copiável** que facilita compartilhar a sala com outros jogadores.

**Como usar:**

1. Ao criar a sala, procure o botão "Copiar Link" na interface
2. Clique para copiar o link completo (ex: `http://26.123.45.67:8000`)
3. Compartilhe este link com seus amigos via Discord, WhatsApp, etc.
4. Eles podem simplesmente abrir o link no navegador para entrar na sala

:::tip
Se você configurou o `preferred_vpn` no `config.toml`, o link já virá com o IP correto da sua VPN automaticamente!
:::

## Túneis Públicos (Em Desenvolvimento)

Opções de túnel público como **LocalTunnel**, **Playit.gg** e **Zrok** estão em desenvolvimento e permitirão compartilhar sessões sem necessidade de VPN.

## Próximos Passos

- [Criar Sala](./criar-sala) - Aprenda a criar e configurar uma sala multiplayer
- [Entrar em Sala](./entrar-sala) - Como se conectar a uma sala existente
- [Lobby](../lobby) - Entenda os campos de configuração da sala
