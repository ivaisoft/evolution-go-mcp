# Evolution Go MCP

Servidor MCP local (stdio) para operações selecionadas da API Evolution v2.3.7. Expõe tools, sem resources nem prompts. O nome do pacote e o comando uvx foram mantidos para compatibilidade com instalações existentes.

A API usa o header apikey. Configure EVOLUTION_GO_URL e EVOLUTION_GO_KEY. Aponte EVOLUTION_GO_URL para o endereço da sua instância.

Para o adapter OpenAPI do Obot, importe openapi.yaml e substitua servers[0].url por uma URL alcançável pelo pod do Obot. Em Kubernetes, use o DNS do serviço configurado no seu cluster; fora dele, exponha uma URL HTTPS.

## Configuração via uvx

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
            "EVOLUTION_GO_URL": "http://localhost:8080",
            "EVOLUTION_GO_KEY": "SUA_CHAVE"
          }
        }
      }
    }

O MCP usa números puros nos endpoints de envio. A tool send_link manda o texto e a URL pelo endpoint sendText com linkPreview habilitado. O parâmetro quoted segue o formato da API Evolution: objeto com key e message.

## Tools e parâmetros

| Tool | Parâmetros |
| --- | --- |
| instances | — |
| create_instance | name, token?, integration? (WHATSAPP-BAILEYS por padrão) |
| connect | instance, number? |
| pair | instance, phone |
| status | instance |
| qr | instance |
| logout | instance |
| delete_instance | instance (nome da instância) |
| summary | — |
| send_text | instance, number, text, opções de envio, linkPreview? |
| send_media | instance, number, url, type, caption?, filename?, opções de envio |
| send_location | instance, number, lat, lng, name?, address?, opções de envio |
| send_contact | instance, number, fullName, phone, org?, opções de envio |
| send_link | instance, number, url, text, delay?, quoted? |
| send_sticker | instance, number, sticker, opções de envio |
| send_poll | instance, number, question, options, maxAnswer?, delay?, quoted? |
| react | instance, key, reaction |
| edit_message | instance, number, key, message |
| delete_message | instance, remoteJid, id, fromMe, participant? |
| mark_read | instance, number, ids, fromMe? |
| message_status | instance, id |
| set_presence | instance, number, state (composing ou recording), delay? |

As opções de envio são delay?, quoted?, mentionAll? e mentionedJid?. O MCP converte as opções de menção para os everyOne e mentioned, aceitos pela API v2. O OpenAPI lista endpoints reais; helpers como pair, qr, summary e send_link reutilizam essas rotas.

