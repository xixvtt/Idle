<div align="center">

🌐 [English](README.md) | [中文](README.zh.md) | [Español](README.es.md) | [한국어](README.ko.md) | **Português**

# Idle — Monitor de Tokens do Claude Code

**Um monitor em tempo real do uso de tokens e das sessões do [Claude Code](https://claude.com/claude-code), para macOS.**
Uma cápsula translúcida flutua no canto da sua tela e mostra, ao vivo, quantos tokens todas as suas sessões do Claude Code consumiram hoje.

<img src="docs/images/hero.png" alt="Idle, o monitor de tokens do Claude Code, flutuando ao lado de um widget do macOS" width="720" />

[![Last commit](https://img.shields.io/github/last-commit/xixvtt/Idle)](https://github.com/xixvtt/Idle/commits/main)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

</div>

---

## O que é o Idle?

O Idle é um **monitor de uso de tokens do Claude Code**, gratuito e de código aberto. Roda como um overlay translúcido em macOS e acompanha:

- **Total de tokens consumidos hoje** — ao vivo, somando todas as sessões e projetos
- **Lista de sessões ativas** — quais workspaces estão rodando, esperando ou ociosos neste instante
- **Monitoramento multi-sessão** — uma linha por sessão aberta do Claude Code
- **Alertas de conclusão** — você é notificado no instante em que uma tarefa do Claude Code termina

Se você vive em modo YOLO e queima sua cota diária sem perceber, o Idle é a cura. Sem abas de navegador, sem dashboards, sem API key — só um monitor visível direto no desktop.

<div align="center">
  <img src="docs/images/solo.png" alt="Idle em modo ocioso exibindo o total de tokens de hoje" width="380" />
</div>

## Por que usar o Idle com o Claude Code

| Problema | Solução do Idle |
|---|---|
| A Anthropic não expõe uma visão diária de uso de tokens | O Idle lê os transcripts locais do Claude Code e calcula o total de hoje em tempo real |
| Rodar várias sessões `claude` torna o controle impossível | O Idle empilha cada sessão ativa em uma única janela |
| Você só descobre que estourou o limite quando o Claude para de responder | O Idle mostra sua contagem de tokens a todo momento |
| Outros monitores exigem API key ou enviam dados pra nuvem | O Idle é 100% local — zero rede, zero API key |

## Instalação (zero configuração)

Baixe a versão mais recente: **[Página de Releases →](https://github.com/xixvtt/Idle/releases)**

| Mac | Arquivo |
|---|---|
| Apple Silicon (M1/M2/M3/M4) | `Idle-x.x.x-arm64.zip` |
| Intel | `Idle-x.x.x-x64.zip` |

1. Dê dois cliques no zip para extrair `Idle.app`
2. **Clique com o botão direito em `Idle.app` → Abrir → Abrir** (o app não está assinado — o Gatekeeper pergunta uma vez)
3. Escolha o tema no primeiro arranque
4. Use o Claude Code normalmente — o rastreamento começa na hora

Sem Python, sem terminal, sem editar JSON. O daemon embutido e os hooks do Claude Code se instalam sozinhos.

### "A Apple não pôde verificar se o Idle está livre de malware"

É o Gatekeeper do macOS bloqueando um app sem assinatura. Rode isso no Terminal pra limpar o atributo de quarentena:

```bash
xattr -cr /Applications/Idle.app
# ou, se você descompactou em outro lugar:
xattr -cr ~/Downloads/Idle.app
```

Depois, dê dois cliques em `Idle.app` normalmente.

Se o macOS ainda recusar, abra **Ajustes do Sistema → Privacidade e Segurança**, role até o final — você vai ver "Idle foi bloqueado…" com um botão **Abrir Mesmo Assim**. Clique uma vez.

> O Idle será assinado e notarizado pela Apple em um release futuro. A versão atual não é assinada porque a assinatura Apple Developer custa $99/ano — assim que o Idle tiver usuários suficientes, cobriremos o custo e esses passos somem.

## Requisitos

- macOS 12 ou superior
- [Claude Code](https://claude.com/claude-code) instalado

## Como o Idle monitora o Claude Code (detalhe técnico)

O Idle usa apenas duas fontes de dados locais:

1. **Hooks do Claude Code** — o Claude Code dispara hooks de shell em cada uso de ferramenta, pedido de permissão e finalização de tarefa. O daemon do Idle recebe esses eventos em `127.0.0.1:7777` pra atualizar o estado da sessão em tempo real.
2. **Arquivos JSONL de transcript** — o Claude Code grava o transcript completo em `~/.claude/projects/`. O Idle só parseia o campo `usage` (input + output + cache_creation tokens) de cada mensagem do assistente, filtrado pela data local de hoje.

O total é recalculado a partir desses arquivos no boot e a cada 30 segundos, então sempre está correto — mesmo depois de reiniciar.

## Privacidade

- **Zero tráfego de rede externo.** O daemon escuta apenas em `127.0.0.1`.
- **Sem API key.** O Idle não chama a API da Anthropic.
- **Nunca lê prompts nem respostas.** Só campos numéricos de uso. Garantido por um teste de AST.
- **Código aberto (MIT).** Audite você mesmo.

## Dê uma ⭐ pro repo

Se o Idle te poupa tempo ou dinheiro no Claude Code, dá uma star no repo — é o maior sinal pra outros devs descobrirem o projeto. Issues, PRs e feedback são todos bem-vindos.

---

**Palavras-chave:** Claude Code, monitor de tokens do Claude Code, rastreador de uso do Claude Code, uso de tokens da Anthropic, dashboard do Claude Code, monitorar Claude Code, gerenciador de sessões do Claude Code, rastreador de limite do Claude Code, Claude Code macOS, overlay para Claude Code.
