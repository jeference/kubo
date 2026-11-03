# Estilos Pixar, Mini Pop e Chibi: referências da Jujubit e prompts do Kubo

Teste de 02 e 03/11/2026, só em 2D. As mesmas 21 entradas passaram pelos 3 estilos na Jujubit e no Kubo (GPT Image 2 pela Runware, com o adaptador real do backend).

## O que tem aqui

| Caminho | Conteúdo |
|---|---|
| [comparativo-pixar.jpg](comparativo-pixar.jpg), [comparativo-mini-pop.jpg](comparativo-mini-pop.jpg), [comparativo-chibi.jpg](comparativo-chibi.jpg) | Entrada, Jujubit e Kubo lado a lado. `[V]` marca um caso de validação. |
| [prompts.json](prompts.json) | Versão ajustada dos prompts: `text`, `photo` e `photo_request`, um trio por estilo. O `_COLOR_RULE` entra antes de cada um. Em uso no backend, em `GENERATION["STYLES"]` de `settings.py`. |
| [casos.json](casos.json) | As 21 entradas, com categoria, modo e grupo (ajuste ou validação). |
| `jujubit/<estilo>/` | As 63 referências da Jujubit, em JPG. |
| `entradas/` | As fotos usadas. |

## Entradas

| Categoria | Foto | Texto |
|---|---|---|
| Pessoa | idoso, mulher de chapéu `[V]` | avó, skatista `[V]` |
| Casal (Duo na Jujubit) | casal | noivos `[V]` |
| Animal | cachorro, gato `[V]` | capivara, gato dormindo `[V]` |
| Objeto | carro, hambúrguer `[V]` | câmera, caneca `[V]` |
| Estrutura | Torre Eiffel | castelo |
| Casos-limite | desenho infantil, pelúcia `[V]` | letras "KUBO", robô `[V]` |
| Foto + texto | cachorro + "de chapéu de mago" | |

São 12 casos de ajuste e 9 de validação. Os de validação só rodaram depois que os prompts estavam quase prontos e não motivaram ajustes de estilo.

## Como a Jujubit se comporta

| Assunto | Pixar (`graduation_pixar_new_duo`) | Mini Pop (`graduation_funkopop_new_duo`) | Chibi (`chibi_new_duo`) |
|---|---|---|---|
| Pessoa | Personagem de corpo inteiro, cabeça um pouco maior | Cabeça enorme, olhos pretos redondos, nariz pequeno | Cabeça grande, olhos de anime |
| Casal | Dois personagens, afastados | Dois bonecos lado a lado | Dois personagens abraçados ou de mãos dadas |
| Animal | Continua animal, quase igual ao Free Style | De foto, fica em 4 patas; de texto, fica em pé e de roupa | **Vira humano** com orelhas e cauda |
| Objeto | **Falha:** devolve a foto (carro), vira pessoa (hambúrguer) ou gera foto realista (câmera, caneca) | Vira boneco, com o objeto na cabeça ou no corpo | Vira personagem segurando ou vestindo o objeto |
| Estrutura | **Falha:** Torre Eiffel vira estudante, castelo vira foto | Boneco com o objeto na cabeça | Personagem com o objeto no cabelo ou na roupa |
| Texto "KUBO" | **Falha:** uma placa com o próprio prompt escrito | Boneco com "KUBO" na camiseta | Personagem com "KUBO" no moletom |
| Robô | **Falha:** um menino | Boneco-robô | Menina de armadura robótica |

Das 21 imagens do Pixar, 9 não passam na verificação de fundo liso do backend. No Mini Pop são 2, e no Chibi, 3.

## Decisões nos prompts

- **Seguimos a Jujubit em:** proporções e rostos dos 3 estilos, Chibi humanizando tudo e Mini Pop transformando objetos em bonecos.
- **Não copiamos as falhas do Pixar:** objetos e estruturas continuam sendo o que são, em formato estilizado e sem rosto.
- **Mantivemos a regra de cores do Kubo:** por isso as cores saem mais primárias que as da Jujubit. Não medimos quantas imagens ficam em até 4 cores.
- **Sem nomes de marca nos prompts:** eles descrevem o visual sem citar Pixar ou Funko. A interface usa o rótulo "Pixar".
- **Sem base:** os estilos da Jujubit não trazem base, diferentemente do fluxo de foto atual do Kubo.

## Problemas conhecidos

- **Invenções:** o Mini Pop acrescentou uma rainha ao castelo. O Chibi desenhou um homem de barba na Torre Eiffel.
- **Texto copiado:** no Chibi, a legenda do desenho infantil foi parar na camiseta.
- **Risco de propriedade intelectual:** um "robô amigável" no Mini Pop saiu parecido com o Optimus Prime na v3, embora não tenha se repetido na versão final.
- **Bloqueio da OpenAI:** a palavra "child" no Chibi coincidiu com a recusa do carro, e sumiu nas versões seguintes. A Jujubit também teve uma recusa isolada (`error_response_risk_control`), que não se repetiu.
- **Margem no Chibi:** 3 de 21 imagens ainda tocam a borda (Torre Eiffel, castelo e caneca).

## Limites

- Uma imagem por caso e por estilo, então a variação entre gerações não foi medida.
- A avaliação de semelhança é visual. Só o fundo foi medido.
- Nada passou pelo 3D nem foi impresso.
- O Kubo não tem Solo/Duo: os casais rodaram sem esse controle. Na Jujubit, rodaram em Duo.
