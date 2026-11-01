# Kubo — protótipo de criação do modelo 3D

Protótipo de uma página para validar a UI/UX do fluxo:

```
texto ─► 1 imagem (FLUX.2 klein) ─┐
foto  ────────────────────────────┴─► edição por chat (FLUX.2 klein) ─► Trellis 2 ─► abas 2D/3D + compra (só visual)
```

- `backend/`: Django 5.2 + DRF (mesmas convenções do razantti: django-environ, ports/adapters em `integrations/`, ruff, pytest). Sem banco: imagens e GLBs ficam em `backend/_media/`.
- `frontend/`: Next 15 + Tailwind 3 + TanStack Query + Zustand + react-three-fiber. O Next faz proxy de `/api` e `/media` para o Django.

## Rodando (Windows)

O Python do sistema não é necessário: o `uv` fornece o 3.12.

**Backend** (porta 8000):

```powershell
cd prototipo/backend
uv venv --python 3.12 .venv
uv pip install --python .venv/Scripts/python.exe -e ".[dev]"
.venv/Scripts/python manage.py migrate
.venv/Scripts/python manage.py runserver
```

**Frontend** (porta 3000):

```powershell
cd prototipo/frontend
npm install
npm run dev
```

Abra http://localhost:3000.

Com GNU make instalado, depois da instalação acima basta rodar, de dentro de `prototipo/`, `make backend` e `make frontend` (cada um num terminal).

## Modo real × modo offline

Toda a configuração fica em `backend/.env` (fora do git). Para criar do zero, copie `backend/.env.example` e preencha `RUNWARE_API_KEY`:

| Variável | Padrão | Para quê |
|---|---|---|
| `RUNWARE_API_KEY` | — | Chave da Runware |
| `GENERATION_ADAPTER` | `integrations.adapters.runware.RunwareGenerationAdapter` | Use `integrations.adapters.runware_stub.StubGenerationAdapter` para testar a UI sem gastar créditos (imagens desenhadas localmente + GLB de exemplo) |
| `RUNWARE_IMAGE_MODEL` | `runware:400@2` (FLUX.2 [klein] 9B) | Trocar se a qualidade/entendimento de português não for suficiente |
| `RUNWARE_3D_MODEL` | `microsoft:trellis-2@4b` | Imagem → 3D |
| `TRELLIS_PRESET` | `low` | Qualidade do 3D: `low` (~US$ 0,01), `medium` (~US$ 0,02), `high` (~US$ 0,05–0,08). Os presets ficam em `TRELLIS_PRESETS`, em `backend/config/settings.py` |

Os templates que envolvem a descrição e a instrução de edição do usuário ficam em `GENERATION["PROMPT_TEMPLATE"]` e `GENERATION["EDIT_PROMPT_TEMPLATE"]`, em `backend/config/settings.py`.

Os tamanhos e preços da tela de compra são valores de exemplo, em `frontend/src/features/creator/lib/sizes.ts`.

> A Runware exige saldo mínimo por tarefa (≈ 1 crédito para o 3D). Sem saldo, as chamadas retornam `insufficientCredits` e a UI mostra o erro.

## Testes e lint

```powershell
cd prototipo/backend;  .venv/Scripts/python -m pytest; .venv/Scripts/ruff check .
cd prototipo/frontend; npm run typecheck; npm run lint
```
