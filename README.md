# Evolution Go MCP

Servidor MCP local (stdio) para as 24 operações da skill `int-evolution-go`. Expõe somente tools; não registra resources nem prompts. As credenciais são lidas do ambiente e enviadas diretamente à Evolution Go REST API.

## Configuração

Configure `EVOLUTION_GO_URL` e `EVOLUTION_GO_KEY` no ambiente do cliente MCP. Exemplo de configuração:

```json
{
  "mcpServers": {
    "evolution-go": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/ivaisoft/evolution-go-mcp",
        "evolution-go-mcp"
      ],
      "env": {
        "EVOLUTION_GO_URL": "https://go.evolution-api.com",
        "EVOLUTION_GO_KEY": "SUA_CHAVE"
      }
    }
  }
}
```

O `uvx` baixa o projeto e suas dependências na primeira execução. Também é possível executar da cópia local com `uv run evolution-go-mcp`.

## Tools e parâmetros

| Tool | Parâmetros |
| --- | --- |
| `instances` | — |
| `create_instance` | `name`, `token?` |
| `connect` | `phone`, `webhook`, `immediate?`, `subscribe?` (lista) |
| `disconnect` | — |
| `status` | — |
| `qr` | — |
| `pair` | `phone` |
| `logout` | — |
| `delete_instance` | `instanceId` |
| `delete_proxy` | `instanceId` |
| `summary` | — |
| `send_text` | `number`, `text`, opções de envio |
| `send_media` | `number`, `url`, `type`, `caption?`, `filename?`, opções de envio |
| `send_location` | `number`, `lat`, `lng`, `name?`, `address?`, opções de envio |
| `send_contact` | `number`, `fullName`, `phone`, `org?`, opções de envio |
| `send_link` | `number`, `url`, `text`, `title?`, `description?`, `imgUrl?`, opções de envio |
| `send_sticker` | `number`, `sticker`, opções de envio |
| `send_poll` | `number`, `question`, `options` (lista), `maxAnswer?`, opções de envio |
| `react` | `number`, `id`, `reaction` |
| `edit_message` | `chat`, `id`, `message` |
| `delete_message` | `chat`, `id` |
| `mark_read` | `number`, `ids` (lista) |
| `message_status` | `id` |
| `set_presence` | `number`, `state` (`composing` ou `recording`), `isAudio?` |

As opções de envio são `delay?`, `quoted?` (objeto JSON), `mentionAll?` e `mentionedJid?` (lista). Números de telefone sem JID recebem o sufixo `@s.whatsapp.net`, como no cliente original.
