# Kubo

Plataforma que conecta quem quer comprar objetos impressos em 3D a parceiros que os imprimem. O cliente descreve o que quer ou envia uma foto, ajusta a imagem conversando com a IA e compra a peça direto da imagem.

- **Produto:** [docs/PRD.md](docs/PRD.md)
- **Arquitetura:** [docs/ARQUITETURA.md](docs/ARQUITETURA.md)

## Estrutura

| Pasta | O que é |
|---|---|
| `apps/backend` | API Django, webhooks, worker de geração e tarefas agendadas |
| `apps/web/consumer` | App do cliente (Next.js) |
| `apps/web/packages` | Código web compartilhado: `ui`, `web-core`, `analytics` |
| `packages` | Contrato e identidade: `api-types`, `api-client`, `design-tokens` |
| `prototipo/` | Protótipo anterior. Fica até a remoção combinada |

## Rodar localmente

Requer Node 20 ou superior, [uv](https://docs.astral.sh/uv/) e make. **A geração usa a Runware de verdade e gasta créditos**: preencha as chaves em `apps/backend/.env`.

```sh
make install
cp apps/backend/.env.example apps/backend/.env
cp apps/web/consumer/.env.example apps/web/consumer/.env.local
```

Em terminais separados:

```sh
make db         # Postgres local na porta 5433, sem Docker
make migrate    # só na primeira vez e a cada migração nova
make backend    # API em :8000
make worker     # executa as gerações
make frontend   # app em :3000
make scheduler  # opcional: expira PIX e aplica a retenção
```

Reinicie `make backend` e `make worker` sempre que mudar o `.env`.

### Fornecedores

| Capacidade | No `.env` local | Depende de |
|---|---|---|
| Imagem | Runware, real | `RUNWARE_API_KEY` |
| Endereço por CEP | ViaCEP, real | Nada |
| Pagamento | **Simulado** | Chaves da AbacatePay |
| Frete | **Simulado** | Credenciais do Melhor Envio |
| Arquivos | Disco local | Credenciais da AWS |
| E-mail | Terminal de `make backend` | Dados de SMTP |

Os nomes das classes reais estão em `.env.example`. Só os testes automatizados usam geração simulada.

Enquanto o pagamento for simulado, confirme um PIX com:

```sh
cd apps/backend && .venv/Scripts/python manage.py simulate_pix_payment KB...
```

Para receber webhooks da AbacatePay, registre `https://SEU-DOMINIO/api/webhooks/abacatepay/?webhookSecret=SEU_SEGREDO` no painel dela, com o mesmo segredo em `ABACATE_PAY_WEBHOOK_SECRET`.

## Comandos

| Comando | O que faz |
|---|---|
| `make test` | Testes do backend e do frontend |
| `make lint` | ruff, ESLint e TypeScript |
| `make fmt` | Formatação |
| `make types` | Regera o OpenAPI e os tipos. Rode a cada mudança de contrato |
| `make build` | Build de produção do app |

## Regras do projeto

As regras estão na seção 1 da [arquitetura](docs/ARQUITETURA.md). Em resumo: o backend decide tudo, a lógica fica em services, toda mudança de status passa pela máquina de estados, só `payments` escreve dinheiro, e toda capacidade externa fica atrás de um port.
