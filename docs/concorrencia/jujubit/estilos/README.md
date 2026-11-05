# Estilos Pixar, Mini Pop e Chibi: referências da Jujubit e prompts do Kubo

Teste de 02 e 03/11/2026, só em 2D. As mesmas 21 entradas passaram pelos 3 estilos na Jujubit e no Kubo (GPT Image 2 pela Runware, com o adaptador real do backend).

## O que tem aqui

| Caminho | Conteúdo |
|---|---|
| [comparativo-pixar.jpg](comparativo-pixar.jpg), [comparativo-mini-pop.jpg](comparativo-mini-pop.jpg), [comparativo-chibi.jpg](comparativo-chibi.jpg) | Entrada, Jujubit e Kubo lado a lado. `[V]` marca um caso de validação. As imagens do Kubo são de antes do plano de cores, então têm mais cores e detalhes que as atuais. |
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
- **Mantivemos a regra de cores do Kubo e acrescentamos um plano de cores:** por isso as cores saem mais primárias e as roupas mais lisas que na Jujubit. Veja a seção seguinte.
- **Sem nomes de marca nos prompts:** eles descrevem o visual sem citar Pixar ou Funko. A interface usa o rótulo "Pixar".
- **Sem base:** os estilos da Jujubit não trazem base, diferentemente do fluxo de foto atual do Kubo.

## Limite de 4 cores

Teste de 03/11/2026, com 19 entradas e uma imagem por caso, contando a olho. Os prompts agora terminam com um plano que diz quais partes dividem a mesma cor, em `_COLOR_PLAN` de `settings.py`, e não pedem mais para manter as cores e o tom de pele da foto.

| Estilo | Imagens em até 4 cores, antes | Depois |
|---|---|---|
| Mini Pop | 7 de 18 | 15 de 18 |
| Chibi | 2 de 18 | 14 de 18 |

Pixar e Livre melhoraram na mesma direção, mas não foram contados. A foto de uma pessoa de camisa estampada saiu em preto, bege, azul e cinza nas 3 repetições, em Mini Pop e em Chibi.

- **Sem garantia:** casais, hambúrguer e capivara de roupa ainda passam de 4 cores.
- **Perda de fidelidade:** as estampas somem, e o modelo às vezes escolhe cores que não estavam na foto, como camisa rosa e calça roxa no casal, ou um gato alaranjado que saiu marrom.
- **Robô instável:** em texto, "um robô amigável" já variava antes e virou caixa de correio, micro-ondas e menina-gato. Não sabemos se o plano piora isso.
- **Segunda etapa descartada:** repintar a imagem com 4 cores nomeadas reduziu mais as cores, mas deixou olhos vazios no Chibi, um cachorro rosado e o cabelo errado, além de dobrar custo e tempo.
- **Paleta:** esses números são de antes da cor de pele clara (`light skin`, `#EBC8B0`), o PLA "Bege Caucasiano" da Voolt3D. A fabricante não publica o código, então ele foi extraído da foto do produto e precisa ser conferido num carretel real. Em 12 imagens de teste, a pele continuou mais alaranjada que esse tom, e a pele escura continuou em marrom. Ainda não há caramelo, e pelos dourados variam entre branco, laranja e marrom.
- **Contagem a olho:** as métricas automáticas que testamos falharam, confundindo sombra com cor ou juntando cores diferentes.

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
