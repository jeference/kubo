# Gere na Tripo, prepare na Meshy

Use a **Tripo para gerar o modelo final**, a **Meshy para checar, reparar e preparar o arquivo de impressão**, e mantenha **Trellis 2 no preview e FLUX.2 klein na edição 2D**. A separação existe porque cada provedor documenta o que falta ao outro: a Tripo documenta `face_limit` de até 1,5 milhão de triângulos, `flatten_bottom` e `model_seed`, mas nenhuma checagem de impressão, reparo geral ou 3MF multicolor; a Meshy documenta análise gratuita, reparo "watertight", redimensionamento e 3MF multicolor, mas limita `target_polycount` a 300 mil e seus termos proíbem dados que identifiquem uma pessoa nos inputs. Nenhum dos dois substitui o preview de cerca de US$ 0,01: o preview mais barato custa de 6 a 10 vezes mais na Meshy e 20 vezes mais na Tripo. Pelos meus cálculos, a jornada recomendada custa de **US$ 0,55 a US$ 1,12 por pedido** em API com 10 previews, sem contar a assinatura mínima de US$ 20 por mês da Meshy. Minha confiança é alta em manter preview e edição, e média em dividir geração e preparação, porque nenhum endpoint foi chamado e a passagem de um arquivo da Tripo para a Meshy só é sustentada pelos formatos de entrada documentados. **Nada disso vale antes de autorização por escrito:** a s. 3.2 da Tripo e as ss. 2.2, 2.6(v) e 1.2 da Meshy atingem diretamente o modelo da Kubo. Documentação não prova qualidade de malha nem estanqueidade; a seção final lista os testes, de cerca de US$ 28 em créditos, que decidem isso.

## Trellis fica no preview, Tripo gera o final, Meshy prepara a impressão

Os oito requisitos avaliados foram inferidos dos arquivos do projeto e não vieram de uma lista formal de requisitos sua. O preço de US$ 0,01 do Trellis, o FLUX.2 klein e a configuração da Jujubit vêm desse mesmo contexto e não foram auditados nas notas.

| Etapa | Usar | Motivo decisivo | Confiança |
|---|---|---|---|
| Preview, gerado muitas vezes antes da venda | Trellis 2 na Runware, sem troca | Mínimo de 5 créditos na Meshy (US$ 0,0625 a US$ 0,10) e 20 na Tripo (US$ 0,20) | Alta no preço; qualidade não comparada |
| Edição por chat | FLUX.2 klein em 2D, com 3D regenerado depois | Nenhum dos dois documenta edição de geometria por instrução de texto | Alta |
| Modelo final, após a compra | Tripo H3.1 (`v3.1-20260211`) em `POST /v3/generation/image-to-model`, da mesma imagem | `face_limit` documentado até 1,5M; a Meshy documenta 300k como alvo máximo; a s. 2.2 da Meshy pesa contra enviar fotos | Média |
| Base plana | `flatten_bottom` em `POST /v3/models/convert` (Tripo) | É o único provedor que documenta esse parâmetro para modelos genéricos | Média; resultado físico não testado |
| Análise, reparo, escala, 3MF | Meshy: `print/analyze`, `print/repair`, `resize`, `convert`, `print/multi-color`, todos aceitando `model_url` | A Tripo não documenta equivalente | Média-baixa até testar a passagem entre provedores |
| Persistência | Armazenamento próprio da Kubo, baixando assim que a tarefa concluir | URLs temporárias nos dois; arquivos da Meshy somem em 3 dias | Alta |

A divisão é sustentada por um fato pouco óbvio das páginas de referência: **as rotas de impressão da Meshy aceitam arquivos externos por `model_url`**. Analyze e Repair aceitam `.glb`, `.gltf`, `.obj`, `.fbx` e `.stl` por URL até 400 MB, e Multi-Color aceita `.glb` ou `.fbx` ([Analyze](https://docs.meshy.ai/api/analyze-printability); [Repair](https://docs.meshy.ai/api/repair-printability); [Multi-Color](https://docs.meshy.ai/api/multi-color-print)). Por isso a preparação não obriga a gerar na Meshy. Como a análise é gratuita, ela pode decidir pedido a pedido se o reparo, que custa 10 créditos e apaga texturas, é necessário.

Há uma segunda vantagem, e esta é inferência minha: com Trellis e FLUX na frente do cliente, Tripo e Meshy só são chamadas pelo backend da Kubo depois da compra, uma vez por pedido. Isso enfraquece, sem eliminar, a leitura de que a Kubo estaria disponibilizando o serviço a "end users". Em contrapartida, a mesma pergunta jurídica passa para a Runware, cujos termos não fazem parte destas notas.

**O argumento mais forte contra a mistura** é a simplicidade da Meshy sozinha: um fornecedor, encadeamento por `input_task_id`, conversão a 1 crédito e análise integrada. Ela não é a recomendação por três motivos: nenhum parâmetro aceita 1,2M de faces, a contagem da saída sem remesh não está documentada ([Image to 3D](https://docs.meshy.ai/api/image-to-3d)), e a s. 2.2 torna a foto do cliente um problema contratual direto. **O argumento mais forte contra a Tripo sozinha** é o próprio requisito 5: a loja é de objetos físicos, e a Tripo não documenta garantia de malha fechada, reparo geral ou multicolor. Se a Kubo só puder contratar um fornecedor hoje, escolha a Meshy para entradas sem pessoas (texto, ilustrações) e a Tripo apenas se houver um reparo local próprio, opção que estas notas não avaliaram.

| Se isto acontecer | A recomendação muda para |
|---|---|
| A Meshy autoriza por escrito fotos de pessoas e revenda, e os testes mostram detalhe suficiente com `geometry_resolution` ou sem remesh | Meshy sozinha no final e na preparação |
| A Holymolly (Tripo) nega a autorização da s. 3.2 | Meshy com contrato próprio (Order), ou nenhum dos dois para fotos |
| A saída H3.1 passa em Analyze de forma consistente e o produto dispensa multicolor | Tripo sozinha, com checagem local, dispensando a assinatura Meshy |
| A Meshy recusa malhas de terceiros, ou trata malhas de rostos como dado pessoal da s. 2.2 | Reparo local, ou Meshy apenas para entradas sem pessoas |
| O modelo final diverge demais do preview Trellis aprovado pelo cliente | Reavaliar o preview com `meshy-6-lite` ou com a mesma família do modelo final, aceitando custo de 6 a 30 vezes maior |
| Multi-Color rejeita as texturas PBR da Tripo | Gerar sem textura na Tripo e usar Retexture da Meshy (mais 10 créditos), ou gerar o modelo colorido na Meshy |

## Só a impressão separa de fato os dois provedores

O status abaixo distingue o que está em página oficial, o que só existe em SDK ou CLI e o que não foi encontrado. Custos em créditos; a Tripo cobra US$ 0,01 por crédito e a Meshy de US$ 0,0125 a US$ 0,02, conforme o plano ([Tripo pricing](https://developers.tripo3d.ai/en/pricing); [Meshy pricing](https://www.meshy.ai/pricing)).

| Requisito | Provedor | O que oferece | Endpoint | Custo | Status |
|---|---|---|---|---|---|
| 1. Texto ou imagem para 3D | Tripo | Texto, imagem, 2 a 4 vistas; séries H e P | `POST /v3/generation/text-to-model`, `image-to-model`, `multiview-to-model` | H3.1: texto 10 a 40; imagem 20 a 50 | Documentado |
| | Meshy | Texto (preview e refine), imagem, 1 a 4 imagens | `POST /openapi/v2/text-to-3d`, `POST /openapi/v1/image-to-3d`, `multi-image-to-3d` | Malha 5 ou 20; imagem com textura 15 a 35; Ultra +5 | Documentado |
| 2. Preview barato | Tripo | H3.1 sem textura, cerca de 40 s | `image-to-model` | 20; com textura 30 | Documentado |
| | Meshy | `meshy-6-lite` (40 s), `meshy-t2` (4 s), `meshy-t2.5` (tempo não publicado), medianas | `image-to-3d` | 5; com textura 2K, 15 | Documentado |
| 3. Final da mesma imagem | Tripo | Nova tarefa; `model_seed` dá malha idêntica apenas com a mesma entrada; refine aposentado | `image-to-model` | 30 a 70 | Documentado; vínculo com o preview: não documentado |
| | Meshy | Nova tarefa; sem `seed` nesse endpoint; refine só texturiza preview de Text to 3D | `image-to-3d` | 30 a 40 | Documentado; vínculo com o preview: não documentado |
| 4. Edição por chat | Tripo | 2D com prompt e máscara; textura por prompt | `image-to-image`, `POST /v3/openai/images/edits`, `POST /v3/models/texture` | 2D 5 a 50; textura 10 a 30 | Documentado; concorrência de imagem é 1 |
| | Tripo | Refaz região por `bbox` e `ref_image`, sem prompt | `POST /v3/mesh/edit` | Não documentado; "billed" no CLI, sem valor | Página fora do índice, status não declarado |
| | Meshy | 2D por prompt; textura por prompt | `POST /openapi/v1/image-to-image`, `retexture` | 2D 3 a 12; textura 10 ou 15 | Documentado |
| | Meshy | Edição de geometria por instrução | Nenhum; pincel de textura só no web app | n/d | Não documentado |
| 5a. STL e 3MF | Tripo | Via conversão | `POST /v3/models/convert` | 5 ou 10 | Documentado |
| | Meshy | `target_formats` ou conversão | `POST /openapi/v1/convert` | Incluso ou 1 | Documentado |
| 5b. Estanque ou reparo | Tripo | Sem garantia nem checagem; `check_printable` só citado no guia de migração; `quick_cap` só após segmentação | `mesh/segment` + `mesh/complete` | 40 + 30 a 50 | Garantia: não documentada; "watertight": só no CLI |
| | Meshy | Análise de malha e paredes; reparo devolve "a watertight version ready to print", removendo texturas | `POST /openapi/v1/print/analyze`, `print/repair` | Grátis; 10 | Documentado; saída bruta sem garantia |
| 5c. Escala real | Tripo | `auto_size` em metros na geração; `scale_factor` multiplicador; sem altura-alvo | `image-to-model`, `convert` | Incluso; 10 | Parcialmente documentado |
| | Meshy | `resize_height` ou `resize_longest_side` em metros | `POST /openapi/v1/resize` | 1 | Documentado; unidade do STL convertido: não documentada |
| 5d. Base plana | Tripo | `flatten_bottom`, `flatten_bottom_threshold`, `pivot_to_center_bottom` | `convert` | 10 | Documentado; suporte adicional (base) não |
| | Meshy | `origin_at: bottom` só move a origem | `resize` | 1 | Achatamento: não documentado |
| 5e. Multicolor | Tripo | 3MF "single color" (fontes em conflito); rota por OBJ com cor de vértice | `convert` | 5 ou 10 | 3MF multicolor: não documentado; rota: só no CLI |
| | Meshy | 3MF de 1 a 16 cores, preset para 9 marcas; exige modelo texturizado | `POST /openapi/v1/print/multi-color` | 10 | Documentado |
| 6. Figuras de 4 a 15 cm (Jujubit: 300k e 1,2M, PBR GLB, 2048²) | Tripo | v3.1: 1,5M; 2M com `geometry_quality=detailed` (+20); `pbr` padrão ligado; `face_limit` sem sobretaxa listada; série P não atende (teto de 50k) | `image-to-model` | 30 | Documentado; resolução da textura padrão: não documentada |
| | Meshy | `target_polycount` até 300k; `texture_resolution: "2k"` é 2048²; `enable_pbr` | `image-to-3d`, `remesh` | 30 a 35; remesh 5 | 300k: documentado; 1,2M: não documentado |
| 7. Revenda e fotos sob LGPD | Tripo | Direitos ao usuário pago; s. 3.2 exige autorização; seção LGPD na política | n/a | n/a | Documentado, com conflitos |
| | Meshy | Propriedade ao plano pago; ss. 2.2, 2.6(v), 1.2 restritivas; sem menção a LGPD | n/a | n/a | Documentado, com conflitos |
| 8. Django, assíncrono | Tripo | Polling, leitura em lote de 100, webhook assinado por HMAC, SDK Python oficial; sem cancelamento | `GET /v3/tasks/{task_id}`, `POST /v3/tasks/list` | Sem preço listado | Documentado |
| | Meshy | Polling, SSE, webhook sem assinatura documentada; sem chave de idempotência; sem SDK REST oficial | `GET .../{id}`, `GET .../{id}/stream` | Sem preço listado | Documentado |

**O requisito 3 tem um risco que nenhum dos dois resolve.** O plano atual gera o final como tarefa nova, e o que o cliente aprovou em Trellis não terá a mesma geometria. Trocar o preview para o provedor final também não garante isso: a Tripo promete malha idêntica só para "the same seed with the same input" ([Image to Model H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard)), e não se sabe se a promessa resiste a um `face_limit` diferente. A Meshy nem expõe `seed` em Image to 3D ([Image to 3D](https://docs.meshy.ai/api/image-to-3d)). Sugiro prever na interface a aprovação do modelo final antes de imprimir, com o custo já absorvido na venda.

**No requisito 4, `mesh/edit` não serve para chat.** A página não tem parâmetro de prompt ou instrução, apenas `bbox` obrigatório e `ref_image` opcional, e o CLI oficial diz que a etapa "stays hidden" até ser "listed and live" ([mesh-edit](https://developers.tripo3d.ai/en/docs/mesh-edit.md); [tripo-cli 0.9.0](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz)). A edição via imagens da Tripo seria tecnicamente viável, mas a concorrência padrão de geração de imagem é **1** por conta ([Tripo rate limits](https://developers.tripo3d.ai/en/docs/rate-limits)). Na Meshy, tarefas 2D e 3D disputam o mesmo limite ([Meshy rate limits](https://docs.meshy.ai/en/api/rate-limits)). O preço do FLUX.2 klein não consta das notas, portanto esta comparação é de capacidade, não de custo.

**No requisito 5, a ordem das operações importa.** Repair remove as texturas, e Multi-Color rejeita modelo sem textura com `model_missing_texture`, de modo que a cadeia colorida com reparo passa obrigatoriamente por Retexture; o efeito disso sobre a estanqueidade não está documentado ([Repair](https://docs.meshy.ai/api/repair-printability); [Errors](https://docs.meshy.ai/api/errors)). Para escala, 4 a 15 cm equivalem a `resize_height` de 0,04 a 0,15 (conversão minha). A parede mínima muda com a impressora: FDM 1,0 mm, SLA 0,8 mm, full color 2,0 mm, com erro quando mais de 5% da superfície fica fina demais ([Analyze](https://docs.meshy.ai/api/analyze-printability)). É preciso enviar `intended_print_height_mm` no caso de figuras pequenas, porque na API v2 o padrão assume "an FDM print 150 mm tall". A v2 também reduz STL e 3MF de Image to 3D a no máximo 150 mm no maior lado, exatamente o teto da Kubo, sem limitar tarefas de Resize ([v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference)).

**No requisito 8, três detalhes afetam o desenho no Django.** O webhook da Tripo exige resposta 2xx em cerca de 5 s e assina com HMAC-SHA256, enquanto o da Meshy dá cerca de 25 s, pode chegar duplicado ou fora de ordem, e não tem assinatura documentada, o que favorece reconsultar a tarefa ao receber o evento ([Tripo webhooks](https://developers.tripo3d.ai/en/docs/webhooks); [Meshy webhooks](https://docs.meshy.ai/api/webhooks)). `credits_consumed` da Tripo é decimal e não pode ser lido como inteiro ([Tripo changelog](https://developers.tripo3d.ai/en/docs/changelog)). E um webhook novo da Meshy "starts on v2 unless you pick v1", mesmo quando a tarefa foi criada na v1 ([v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference)). Recomendo integrar as rotas `print/*` pela v1, que tem páginas de referência, isolando o cliente da Meshy em um adaptador, pois a v2 muda o formato das respostas e essas rotas só existem nela por regra declarada.

## A jornada recomendada custa menos de US$ 1,15 por pedido, mas previews e assinatura pesam mais

Todos os valores abaixo são **cálculos meus**, feitos com os preços das notas ([Tripo pricing](https://developers.tripo3d.ai/en/pricing); [Meshy API pricing](https://docs.meshy.ai/api/pricing); [Meshy pricing](https://www.meshy.ai/pricing)). Premissas: 10 previews por cliente; US$ 0,01 por preview Trellis (valor do briefing); nenhuma regeneração por resultado ruim, embora tarefas bem-sucedidas com saída ruim sejam cobradas; Tripo H3.1; Meshy-7.1 sem Ultra, a US$ 0,02 (Pro) ou US$ 0,0125 (Ultra ou Studio 3x e 5x), supondo uso total dos créditos do plano; `face_limit` sem sobretaxa, porque nenhuma é listada. Não incluem FLUX.2 klein, armazenamento, impostos, câmbio ou impressão física. O caminho "melhor caso" supõe que a Analyze não acuse problema.

| Jornada | Composição em créditos | Pro | Ultra |
|---|---|---|---|
| **Recomendada, uma cor** | Tripo 20 (sem textura) + 10 (STL, base plana); Meshy 12 (Analyze 0, Repair 10, Resize 1, Convert 1) | **US$ 0,64** | **US$ 0,55** |
| **Recomendada, multicolor, melhor caso** | Tripo 30 + 10 (FBX, base plana); Meshy 11 (Analyze 0, Resize 1, Multi-Color 10) | **US$ 0,72** | **US$ 0,64** |
| **Recomendada, multicolor, com reparo** | Tripo 30 + 10; Meshy 31 (acima + Repair 10 + Retexture 10) | **US$ 1,12** | **US$ 0,89** |
| Tripo sozinha, sem reparo nem checagem | Tripo 20 + 10 | US$ 0,40 | n/a |
| Tripo sozinha, com a receita de furos do CLI | Tripo 20 + 40 + 30 a 50 + 10 | US$ 1,10 a US$ 1,30 | n/a |
| Meshy sozinha, uma cor, sem base plana | Meshy 20 + 12 | US$ 0,74 | US$ 0,50 |
| Meshy sozinha, multicolor, melhor caso e com reparo | Meshy 41 ou 61 | US$ 0,92 ou US$ 1,32 | US$ 0,61 ou US$ 0,86 |

Ultra geometry soma 5 créditos à Meshy (US$ 0,10 ou US$ 0,0625). Na Tripo, `geometry_quality=detailed` soma 20 (US$ 0,20) e só é necessário acima de 1,5M; 1,2M cabe no padrão da v3.1 ([Image to Model H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard)). O multicolor com reparo descarta a textura paga na Tripo; sabendo disso de antemão, gerar sem textura economiza 10 créditos.

**A troca do preview é a decisão de maior impacto financeiro, e o motivo aparece no custo por venda, não por cliente.** A tabela usa uma hipótese ilustrativa, não um dado da Kubo: 10 previews por cliente e 1 venda a cada 20 clientes, ou seja, 200 previews por venda.

| Preview | Por unidade | 10 previews | 200 previews por venda | Múltiplo do Trellis |
|---|---|---|---|---|
| Trellis 2 (briefing) | US$ 0,01 | US$ 0,10 | **US$ 2,00** | 1x |
| Meshy `meshy-6-lite`, `meshy-t2` ou `meshy-t2.5`, só malha | US$ 0,0625 a US$ 0,10 | US$ 0,63 a US$ 1,00 | **US$ 12,50 a US$ 20,00** | 6,25x a 10x |
| Mesmos modelos, textura 2K | US$ 0,19 a US$ 0,30 | US$ 1,88 a US$ 3,00 | **US$ 37,50 a US$ 60,00** | 19x a 30x |
| Tripo H3.1, imagem, sem textura | US$ 0,20 | US$ 2,00 | **US$ 40,00** | 20x |
| Tripo H3.1, imagem, textura padrão | US$ 0,30 | US$ 3,00 | **US$ 60,00** | 30x |

As notas não dizem se o preview Trellis vem texturizado, e isso define qual linha é a comparação justa. Mesmo no melhor cenário, a troca só se paga se o Trellis estiver causando perda de vendas ou divergência inaceitável com o final.

**A assinatura muda a conta em volumes baixos.** A API da Meshy exige plano Pro ou superior, e os créditos mensais não acumulam: "Features do not roll over from one month to the next" ([Meshy Terms](https://www.meshy.ai/terms-of-use); [Meshy API](https://www.meshy.ai/api)). O Pro de US$ 20 cobre cerca de 83 pedidos a 12 créditos ou 32 pedidos a 31 créditos por mês. Com 10 pedidos no mês, a Meshy custa US$ 2,00 por pedido, levando a jornada de uma cor a **US$ 2,40**, não US$ 0,64. A Tripo vende crédito pré-pago a partir de US$ 1, sem assinatura ([Tripo pricing](https://developers.tripo3d.ai/en/pricing)). O preço de pacotes extras da Meshy não pôde ser verificado sem login, portanto o custo acima da franquia é desconhecido. O plano Ultra de US$ 100 não apareceu na tabela de preços como ela foi obtida na pesquisa; se não puder ser comprado do Brasil, a taxa de US$ 0,0125 exige Studio de US$ 210 ou US$ 350 por mês.

## Cláusulas que podem bloquear o negócio antes de qualquer teste técnico

**Isto não é aconselhamento jurídico.** São notas de leitura para levar a um advogado. O ponto central: os dois contratos concedem direitos amplos sobre as saídas em planos pagos, mas têm cláusulas sobre usuários finais, revenda de acesso e dados pessoais que atingem a operação da Kubo. As páginas de marketing e ajuda dizem coisas mais amigáveis do que os termos, e a Meshy tem cláusula de acordo integral (s. 11.10) que favorece a leitura dos termos.

### Tripo (Holymolly Ltd, termos de 11 de julho de 2025)

**s. 3.2, usuários finais:**

> "You shall not, and shall not permit any third party to: [...] make the Generative 3D Foundation Model Service available to any third party, including end users, without the prior written authorization and consent of Holymolly."

**s. 3.1, atividade comercial:**

> "(a) take any action or (b) make available any Inputs on or through Tripo that: [...] involves commercial activities and/or sales, such as contests, sweepstakes, barter, advertising, or pyramid schemes without Company's prior written consent"

**s. 3.2, concorrência:**

> "use Outputs generated by the Services to create models or services that directly compete with Holymolly and its models, products and services. However, that you may use Outputs for lawful commercial or non-commercial purposes, so long as such Outputs are not distributed or made available to third parties in a manner inconsistent with this Agreement or applicable laws"

Todas estão em [Tripo Terms](https://www.tripo3d.ai/terms). **O conflito é com a própria central de ajuda**, que lista "3D print and sell physical products: Yes" e "Print-on-demand products: Yes", mas se declara "a simplified summary" e repete a restrição: "Redistribute via the Tripo Generative 3D Foundation Model Service to third parties without written authorization: No" ([Commercial use guide](https://www.tripo3d.ai/help/privacy-policy/how-to-use-tripo-models-commercially)). A vantagem da s. 3.2 é ter um caminho explícito: autorização escrita. Em dados, a política de setembro de 2026 tem seção LGPD, encarregado nomeado e transferência sob o Art. 33, mas diz "Somos o controlador dos seus dados pessoais" e pede "You should not submit your own personal information as part of any Input"; ao mesmo tempo, reconhece "Where Inputs depict people, their visual features may be processed" ([Tripo Privacy](https://www.tripo3d.ai/privacy)). A sentença "When we process personal information on behalf of an enterprise customer, that customer is responsible for its processing" sugere que o papel de operador depende de relação enterprise. Não há prazo de retenção publicado para a API: a FAQ traz literalmente "Tripo will retain user inputs and generated data for XXX." ([Support FAQ](https://docs.tripo3d.ai/other/support-faq.html)).

### Meshy (Meshy LLC, termos de 19 de setembro de 2026)

**s. 2.2, dados pessoais nos inputs**, o maior bloqueio para fotos:

> "You agree that you will not include any personally identifiable information about yourself or any third party in your Customer Input, including but not limited to financial information, Social Security numbers, physical address or any other data that could identify a specific person."

**s. 2.4, identificadores nas saídas:**

> "The Service may include machine-readable metadata, digital watermarks, or other identifiers in Customer Output to identify that the Customer Output was generated by AI. You agree not to remove, alter, disable, or otherwise tamper with such identifiers."

**s. 2.6, usos proibidos**, incluindo revenda:

> "You agree you may not use the Service in the following manner or for the following purposes: [...] (iv) develop or offer competitive products or services or engage in competitive analysis; (v) resell or redistribute the Service or access to the Service; (vi) allow multiple users to use one user account; [...] (xi) use generated digital assets to train, develop, or improve AI models that are competitive with Meshy"

**s. 1.2, uso interno:**

> "Depending on your account type, access to and use of the Service is permitted solely for your internal use and only by you, if you are an individual user, or by your employees, contractors, consultants, and agents who are permitted by you to access and use the Service"

**s. 2.9, treinamento:**

> "Meshy may use Customer Inputs and Customer Outputs (collectively, 'User Content') from non-Enterprise Customers to train, validate, test, or improve Services unless otherwise agreed to in the Order. You may opt out of such use by contacting support@meshy.ai."

Todas estão em [Meshy Terms](https://www.meshy.ai/terms-of-use). **Os conflitos são diretos.** Sobre treinamento, a página da API afirma "No. Your API inputs and generated models are never used for training" ([Meshy API](https://www.meshy.ai/api)), e a ajuda fala em dados anonimizados ([Data and training FAQ](https://help.meshy.ai/en/articles/15724182-is-meshy-safe-and-private-data-and-training-faq)). Sobre revenda, a página Enterprise menciona "a platform putting generation in front of its own users", e a página da API lista impressão 3D como caso de uso, o que sugere que esse uso existe por contrato próprio ([Meshy Enterprise](https://www.meshy.ai/enterprise); [Meshy API](https://www.meshy.ai/api)). A Meshy também tem o próprio negócio de impressão: um adendo cobre a "Meshy Shop", e seu AUP diz que "Using Meshy's services to develop any technology or product that is competitive with Meshy or otherwise commercially exploits Meshy is prohibited." ([Meshy AUP](https://www.meshy.ai/acceptable-use-policy)). A política de privacidade não menciona LGPD nem Brasil ([Meshy Privacy](https://www.meshy.ai/privacy-policy)).

**A mistura reduz a exposição, sem eliminá-la.** A foto iria só para Tripo e Runware, mas uma malha texturizada de um rosto enviada à Meshy por `model_url` também é Customer Input e pode ser lida como "data that could identify a specific person". Um STL só de geometria reduz o risco, e o fluxo multicolor o aumenta, porque exige textura. Reparar ou converter pode alterar identificadores da s. 2.4. E enviar saídas da Tripo a outro provedor precisa ser compatível com o trecho "not distributed or made available to third parties in a manner inconsistent". Nas duas empresas a indenização corre do cliente para o provedor, nenhuma indenização do provedor foi encontrada e nenhuma garante exclusividade, de forma que a Kubo não deve prometer design único e precisa de declarações e fluxo de remoção próprios ([Tripo Terms](https://www.tripo3d.ai/terms); [Meshy Terms](https://www.meshy.ai/terms-of-use)). As notas não analisam a LGPD em relação aos parceiros ocultos: nenhum dos contratos trata de impressor terceirizado, e o repasse de dados a eles é pergunta para o advogado.

### O que confirmar por escrito antes de assinar

| Provedor e canal | Pergunta | Cláusula |
|---|---|---|
| Tripo, `business@tripo3d.ai` | Autoriza plataforma em que cliente final dispara geração, direta ou indiretamente, no backend da Kubo? | s. 3.2 |
| Tripo | Revenda de impressões físicas é permitida sob a s. 3.1, com impressão por parceiros não divulgados? | ss. 3.1, 5.2.2 |
| Tripo | Enviar saídas a outro provedor (Meshy) para reparo é aceito? A Kubo é concorrente? | s. 3.2 |
| Tripo | Tripo pode atuar como operadora sob DPA, para plano pré-pago, com fotos de pessoas e menores? | Privacidade, LGPD |
| Tripo | Qual o prazo de retenção de inputs e saídas da API? Como funciona a "scheduled deletion"? | FAQ "XXX" |
| Tripo | Anonimizados de API entram em desenvolvimento de modelos? Créditos promocionais contam como "paid"? | s. 5.2; Privacidade |
| Meshy, `legal@meshy.ai` e vendas | Fotos de pessoas com consentimento são permitidas? E malhas ou texturas de rostos por `model_url`? | ss. 2.2, 2.6(x) |
| Meshy | Back-office de marketplace é revenda de acesso ou uso interno? Exige Enterprise? | ss. 2.6(v), 1.2 |
| Meshy | Marketplace de impressão é produto concorrente, dada a Meshy Shop? | s. 2.6(iv), AUP s. 4 |
| Meshy | Reparar, converter ou fatiar viola o dever sobre identificadores? | s. 2.4 |
| Meshy, `support@meshy.ai` | Enviar antes de qualquer tráfego o assunto "Request to opt out of Meshy data training" e guardar a confirmação | s. 2.9 |
| Meshy | Há DPA para plano self-serve? Vale para o Brasil? Studio tem retenção de 14 dias? | s. 11.4; s. 2.5 |

**Fatos relevantes que não puderam ser verificados:** preço de pacotes extras da Meshy; aceitação de cartão brasileiro, Pix ou Boleto em qualquer dos dois; compra do plano Ultra a partir do Brasil; disponibilidade de DPA em plano self-serve; conteúdo do trust center da Meshy (Drata retornou 403; `trust.meshy.ai` pede login); retenção de imagens de entrada em ambos; regiões de processamento da Tripo além de "United States and other countries"; aumento efetivo de concorrência na Tripo; histórico real de uptime; regras de tributação brasileira sobre importação de serviço, que não foram pesquisadas; e o valor de créditos grátis da Tripo, sem número oficial. Moderação também é opaca nos dois, sem critérios publicados, e passar pelo filtro não equivale a liberar direitos autorais ([Tripo errors](https://developers.tripo3d.ai/en/docs/error-handling); [Meshy errors](https://docs.meshy.ai/en/api/errors)).

## Conflitos entre fontes oficiais seguem sem resolução

Não escolhi versões em silêncio. A coluna final diz como tratar cada conflito até haver resposta do provedor.

| Tema | O que dizem as fontes | Como tratar |
|---|---|---|
| Validade da URL, Tripo | "temporary", sem prazo ([SDK](https://developers.tripo3d.ai/en/docs/sdk)); "~24 hours" ([skill de migração](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md)); "five minutes" ([legado](https://docs.tripo3d.ai/task-query/get-your-task-result.html)); "60 seconds" ([FAQ legada](https://docs.tripo3d.ai/other/support-faq.html)); "~5 minutes" ([CLI](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz)) | Baixar na hora; consultar de novo gera URL nova |
| Retenção, Tripo | "XXX" na FAQ; exclusão ao remover o ativo na [Privacy](https://www.tripo3d.ai/privacy); "scheduled deletion" sem mecanismo na [ajuda](https://www.tripo3d.ai/help/privacy-policy/is-my-asset-safe) | Desconhecida; perguntar |
| Retenção, Meshy | 3 dias nos [termos](https://www.meshy.ai/terms-of-use) e na [documentação](https://docs.meshy.ai/api/asset-retention); 14 dias no Studio na [página da API](https://www.meshy.ai/api) | Assumir 3 dias |
| Expiração de créditos, Meshy | "up to one (1) year" nos termos; "permanent credits do not expire" no [preço](https://www.meshy.ai/pricing) | Assumir 1 ano |
| Expiração de créditos, Tripo | Não expiram ([FAQ atual](https://developers.tripo3d.ai/en); [FAQ legada](https://docs.tripo3d.ai/other/support-faq.html)); pré-pagos e não reembolsáveis ([termos do portal](https://developers.tripo3d.ai/en/terms)) | As fontes lidas não divergem; confirmar em contrato |
| Treinamento, Meshy | Permitido salvo opt-out nos termos; "never" na página da API; anonimizado na ajuda | Fazer opt-out |
| Treinamento, Tripo | Não treina ([termos](https://www.tripo3d.ai/terms), [FAQ](https://developers.tripo3d.ai/en)); dados anonimizados, "including text prompts and Outputs", podem desenvolver modelos ([Privacy](https://www.tripo3d.ai/privacy)) | Perguntar qual vale para API |
| Dados pessoais, Tripo | "does not collect, store, or process users' personal data" ([FAQ legada](https://docs.tripo3d.ai/other/support-faq.html)) contra a descrição de inputs da Privacy | Considerar a Privacy, mais recente |
| Cor do 3MF, Tripo | "single color" ([convert](https://developers.tripo3d.ai/en/docs/models-convert)); "3D printing with color" ([site China](https://developers.tripo3d.com/en/docs/models-convert)); "only exports geometry" ([legado](https://docs.tripo3d.ai/export/conversion.html)) | Assumir sem cor |
| Cor do 3MF, Meshy | Cor por Multi-Color ou partes ([web](https://docs.meshy.ai/webapp/guides/platform/export-formats)); Auto Split "geometry only" ([API](https://docs.meshy.ai/api/auto-split)) | Usar Multi-Color |
| Parede mínima, Meshy | API: FDM 1,0, SLA 0,8, full color 2,0 mm ([Repair](https://docs.meshy.ai/api/repair-printability)); web: FDM 1,2, SLA ou DLP 0,5, SLS 0,8 mm ([guia](https://docs.meshy.ai/webapp/guides/use-cases/3d-printing)) | Validar com parceiros |
| `refine` e `stylize`, Tripo | "retired" ([SDK](https://developers.tripo3d.ai/en/docs/sdk)); ainda em [changelog](https://developers.tripo3d.ai/en/docs/changelog), [migração](https://developers.tripo3d.ai/en/docs/migration-v2-to-v3) e [limites](https://developers.tripo3d.ai/en/docs/rate-limits) | Não usar |
| `mesh/edit`, Tripo | CLI "stays hidden"; MCP "available without" a variável ([tripo-cli 0.9.0](https://registry.npmjs.org/tripo-cli/-/tripo-cli-0.9.0.tgz)) | Não depender |
| `model`, Tripo | Obrigatório na página internacional; padrão `v3.1-20260211` no [site China](https://developers.tripo3d.com/en/docs/generation-image-to-model/standard) | Sempre enviar e fixar |
| Upload, Tripo | 150 MB e `presigned_url` na [documentação](https://developers.tripo3d.ai/en/docs/files-presign); 200 MB e `upload_url` na skill | Testar antes de codificar |
| Convert, Tripo | `face_limit` padrão preserva o original na [página atual](https://developers.tripo3d.ai/en/docs/models-convert), 10000 no [legado](https://docs.tripo3d.ai/export/conversion.html); `quad` força FBX na atual, com nuance no legado | Enviar valores explícitos |
| `should_texture`, Meshy | Recomendado na [referência v2](https://docs.meshy.ai/en/api/migrate-to-v2/reference); "Not generally available yet" no [OpenAPI](https://docs.meshy.ai/openapi.json) | Não depender |
| V2 da Tripo | "scheduled to shut down on 2026-10-31" ([SDK](https://developers.tripo3d.ai/en/docs/sdk)); "can run in parallel" ([migração](https://developers.tripo3d.ai/en/docs/migration-v2-to-v3)) | Integrar só V3 |
| Showcases, Meshy | Código do CLI cita "official docs" e 1 crédito; nada público ([meshy-cli](https://github.com/meshy-dev/meshy-cli)) | Tratar como não documentado |
| SDKs, Meshy | "SDKs available for Python, JavaScript, and Unity" em [llms.txt do site](https://www.meshy.ai/llms.txt); nenhum repositório REST na organização | Escrever cliente próprio |

## Inventário: 28 operações na Tripo, 173 na Meshy v1 e 28 rotas v2

Todos os custos vêm das notas. "Sem preço publicado" significa que nenhuma página consultada menciona cobrança nessa rota.

### Tripo V3: 28 operações com documentação de referência

Base `https://openapi.tripo3d.ai` (China: `https://openapi.tripo3d.com`). O inventário inicial contava 27; a diferença era apenas `mesh/edit`. A página de SDK tem outra lista, com 26 rotas, que soma `image-to-depth` e omite `mesh/edit` e as duas rotas `openai/images/*`.

| # | Método e caminho | O que faz | Custo (créditos) | Doc |
|---|---|---|---|---|
| 1 | `POST /v3/generation/text-to-model` | Texto para 3D, séries H ou P | H3.1: 10, 20, 30, 40 por textura. P2: 100 a 130. P1: 30, 40 | [H](https://developers.tripo3d.ai/en/docs/generation-text-to-model/standard), [P](https://developers.tripo3d.ai/en/docs/generation-text-to-model/p) |
| 2 | `POST /v3/generation/image-to-model` | Imagem para 3D | H3.1: 20, 30, 40, 50. P2: 100 a 130. P1: 40, 50. Adicionais H: geometria HD +20, quad +5, low poly +10, partes +20 | [H](https://developers.tripo3d.ai/en/docs/generation-image-to-model/standard), [P](https://developers.tripo3d.ai/en/docs/generation-image-to-model/p) |
| 3 | `POST /v3/generation/multiview-to-model` | 2 a 4 vistas para 3D | Igual a imagem | [H](https://developers.tripo3d.ai/en/docs/generation-multiview-to-model/standard), [P](https://developers.tripo3d.ai/en/docs/generation-multiview-to-model/p) |
| 4 | `POST /v3/generation/image-to-splat` | Imagem para Gaussian splat (não é malha) | 30 | [doc](https://developers.tripo3d.ai/en/docs/generation-image-to-splat) |
| 5 | `POST /v3/generation/text-to-image` | Texto para imagem | 5 a 50, por modelo e resolução | [doc](https://developers.tripo3d.ai/en/docs/generation-text-to-image) |
| 6 | `POST /v3/generation/image-to-image` | Edição, fusão e estilo de imagem | 5 a 50, por modelo e resolução | [doc](https://developers.tripo3d.ai/en/docs/generation-image-to-image) |
| 7 | `POST /v3/generation/image-to-multiview` | Uma imagem para quatro vistas | 10 | [doc](https://developers.tripo3d.ai/en/docs/generation-image-to-multiview) |
| 8 | `POST /v3/generation/edit-multiview` | Edita vistas geradas | 5 por imagem editada | [doc](https://developers.tripo3d.ai/en/docs/generation-edit-multiview) |
| 9 | `POST /v3/models/texture` | Texturiza ou retexturiza | Fast 10, padrão 10, HD 20, 8K 30 | [doc](https://developers.tripo3d.ai/en/docs/models-texture) |
| 10 | `POST /v3/models/convert` | Exporta GLTF, FBX, USDZ, OBJ, STL, 3MF; achatamento, pivô, escala | 5 básico; 10 com parâmetros avançados | [doc](https://developers.tripo3d.ai/en/docs/models-convert) |
| 11 | `POST /v3/models/import` | Importa modelo externo e o normaliza | Ausente na página atual; "Free" no legado | [doc](https://developers.tripo3d.ai/en/docs/models-import) |
| 12 | `POST /v3/mesh/segment` | Divide em partes | 40 | [doc](https://developers.tripo3d.ai/en/docs/mesh-segment) |
| 13 | `POST /v3/mesh/smartsegment` | Segmentação de ponta a ponta | 85 imagem; 55 modelo | [doc](https://developers.tripo3d.ai/en/docs/mesh-smartsegment) |
| 14 | `POST /v3/mesh/complete` | Completa partes de uma tarefa `mesh/segment` | 50; `quick_cap` 30 | [doc](https://developers.tripo3d.ai/en/docs/mesh-complete) |
| 15 | `POST /v3/mesh/decimate` | Retopologia; teto de 20k triângulos | v3.0: 35 ou 40 (quad). v2.0: 30. v1.0: 10 | [doc](https://developers.tripo3d.ai/en/docs/mesh-decimate) |
| 16 | `POST /v3/mesh/uv` | Refaz UV, até 80 mil triângulos | 20 | [doc](https://developers.tripo3d.ai/en/docs/mesh-uv) |
| 17 | `POST /v3/mesh/edit` | Refaz região por `bbox`, só P2; página não indexada, status não declarado | Não documentado | [doc](https://developers.tripo3d.ai/en/docs/mesh-edit.md) |
| 18 | `POST /v3/animations/rig-check` | Verifica se aceita rig | Grátis | [doc](https://developers.tripo3d.ai/en/docs/animations-rig-check) |
| 19 | `POST /v3/animations/rig` | Rig automático | 25 | [doc](https://developers.tripo3d.ai/en/docs/animations-rig) |
| 20 | `POST /v3/animations/retarget` | Aplica animações predefinidas | 10 por animação | [doc](https://developers.tripo3d.ai/en/docs/animations-retarget) |
| 21 | `GET /v3/tasks/{task_id}` | Consulta tarefa | Sem preço publicado | [doc](https://developers.tripo3d.ai/en/docs/task-query) |
| 22 | `POST /v3/tasks/list` | Lê até 100 IDs informados | Sem preço publicado | [doc](https://developers.tripo3d.ai/en/docs/task-batch-query) |
| 23 | `POST /v3/files` | Upload multipart, devolve `file_token` | Sem preço publicado | [doc](https://developers.tripo3d.ai/en/docs/files) |
| 24 | `POST /v3/files/presign` | URL pré-assinada para arquivos grandes | Sem preço publicado | [doc](https://developers.tripo3d.ai/en/docs/files-presign) |
| 25 | `GET /v3/account/balance` | Saldo e créditos congelados | Sem preço publicado | [doc](https://developers.tripo3d.ai/en/docs/account.md) |
| 26 | `GET /v3/account/usage` | Consumo por tarefa; `limit` e `offset` só na skill e no SDK | Não documentado | [account](https://developers.tripo3d.ai/en/docs/account.md), [billing](https://developers.tripo3d.ai/en/docs/billing.md) |
| 27 | `POST /v3/openai/images/generations` | Geração compatível com OpenAI | "same credits" das rotas nativas | [doc](https://developers.tripo3d.ai/en/docs/openai-compat-images.md) |
| 28 | `POST /v3/openai/images/edits` | Edição compatível com OpenAI, com `mask`; só `gpt-image-*` | "same credits"; 10 em 1024x1024 `low` é inferência das notas | [doc](https://developers.tripo3d.ai/en/docs/openai-compat-images.md) |

A Tripo envia os eventos `task.completed`, `task.failed` e `balance.low` a um endpoint configurado no console ([webhooks](https://developers.tripo3d.ai/en/docs/webhooks)). Na V3 não foram encontrados cancelamento, exclusão, listagem por filtro, criação em lote nem sandbox. O campo `type` não é mais enviado e só volta na resposta: `text_to_model`, `image_to_model`, `multiview_to_model`, `image_to_splat`, `text_to_image`, `image_to_image`, `image_to_multiview`, `edit_multiview`, `texture_model`, `convert_model`, `import_model`, `mesh_segmentation`, `mesh_completion`, `highpoly_to_lowpoly`, `mesh_uv`, `smartsegment_image`, `animate_prerigcheck`, `animate_rig`, `animate_retarget`. Não existe enum oficial; `mesh_edit` e `smartsegment_model` só aparecem no CLI.

### Tripo V3: 5 rotas sem página de referência

| Método e caminho | Situação | Custo | Rótulo |
|---|---|---|---|
| `POST /v3/generation/image-to-depth` | Tabela da [página de SDK](https://developers.tripo3d.ai/en/docs/sdk.md), só Python | Não documentado | Só em SDK |
| `POST /v3/generation/smartsegment` | Constante em `GatewayDenylist.java` no [SDK Java](https://github.com/Tripo-Developer/tripo-java-sdk); função desconhecida | Não documentado | Só em SDK |
| `POST /v3/files/upload-credentials` | Citada no [changelog](https://developers.tripo3d.ai/en/docs/changelog.md); a página de SDK diz "no public client flow" | Sem preço publicado | Menção apenas, sem parâmetros |
| `POST /v3/models/refine` | "retired" na página de SDK, com menções antigas em outras páginas | n/a | Aposentada; não documentada |
| `POST /v3/models/stylize` | Mesma situação | n/a | Aposentada; não documentada |

Também em SDK: `<consoleApi>/cli/device/code` e `/cli/device/token`, login do CLI em API do console. Outras rotas de `platform.tripo3d.ai` são internas do console e não são oferta pública.

### Tripo V2, legado com desligamento agendado

A retirada estava marcada para **2026-10-31 16:00 UTC**, ontem na data desta pesquisa, e **não foi verificada**. Base `https://api.tripo3d.ai/v2/openapi`, listada só para completude.

| Método e caminho | Fonte |
|---|---|
| `POST /task`; `GET /task/{task_id}` | [Quick start legado](https://docs.tripo3d.ai/get-started/quick-start.html) |
| `POST /upload` | [Migração](https://developers.tripo3d.ai/en/docs/migration-v2-to-v3.md) |
| `POST /upload/sts`; `POST /upload/sts/token` | [Módulo legado](https://platform.tripo3d.ai/assets/upload-sts-XXIAuI4A.js) |
| `POST /upload/temporary_token`; `POST /task/batch`; `POST /user/wallet/usage/detail` | [Skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md) |
| `GET /task/watch/:id`; `/task/watch/all[/:since]` (WebSocket) | [Skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md) |
| `GET /user/balance` e `GET /user/wallet/balance` (fontes divergem) | [Módulo wallet](https://platform.tripo3d.ai/assets/wallet-C0HLJP2u.js); [Skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md) |
| `/provider/bailian/v1/submit`, `/query` (China) | [Skill](https://developers.tripo3d.ai/assets/developer/tripo-v2-to-v3-migration/SKILL.md) |

### Meshy: 88 operações padrão (83 no OpenAPI, 5 só em página)

Base `https://api.meshy.ai`. Cada família tem 5 operações. Criação de tarefa é cobrada; nas rotas de leitura e exclusão não há preço listado. `DELETE` reembolsa tarefa `PENDING`, responde `409` em `IN_PROGRESS` e não reembolsa tarefa concluída ([Text to 3D](https://docs.meshy.ai/api/text-to-3d)). Text to 3D está em caminho `v2`, mas pertence ao conjunto estável e entra nas 173.

| Operações (5 por família) | O que faz | Custo do `POST` (créditos) | Doc |
|---|---|---|---|
| `POST /openapi/v2/text-to-3d`<br>`GET /openapi/v2/text-to-3d`<br>`GET /openapi/v2/text-to-3d/{id}`<br>`DELETE /openapi/v2/text-to-3d/{id}`<br>`GET /openapi/v2/text-to-3d/{id}/stream` | Texto para 3D: preview, refine | Preview 20 (`meshy-7.1`, `meshy-6`) ou 5 (lite, t2, t2.5); Ultra +5; refine 10 ou 15 (8K) | [doc](https://docs.meshy.ai/api/text-to-3d) |
| `POST /openapi/v1/image-to-3d`<br>`GET /openapi/v1/image-to-3d`<br>`GET /openapi/v1/image-to-3d/{id}`<br>`DELETE /openapi/v1/image-to-3d/{id}`<br>`GET /openapi/v1/image-to-3d/{id}/stream` | Imagem para 3D | Malha 5 ou 20; com textura 15 a 35; Ultra +5 | [doc](https://docs.meshy.ai/api/image-to-3d) |
| `POST /openapi/v1/multi-image-to-3d`<br>`GET /openapi/v1/multi-image-to-3d`<br>`GET /openapi/v1/multi-image-to-3d/{id}`<br>`DELETE /openapi/v1/multi-image-to-3d/{id}`<br>`GET /openapi/v1/multi-image-to-3d/{id}/stream` | 1 a 4 imagens para 3D | Malha 5 ou 20; textura 15 (lite), 30 ou 35; Ultra +5 | [doc](https://docs.meshy.ai/api/multi-image-to-3d) |
| `POST /openapi/v1/retexture`<br>`GET /openapi/v1/retexture`<br>`GET /openapi/v1/retexture/{id}`<br>`DELETE /openapi/v1/retexture/{id}`<br>`GET /openapi/v1/retexture/{id}/stream` | Nova textura | 10 (2K, 4K); 15 (8K) | [doc](https://docs.meshy.ai/api/retexture) |
| `POST /openapi/v1/remesh`<br>`GET /openapi/v1/remesh`<br>`GET /openapi/v1/remesh/{id}`<br>`DELETE /openapi/v1/remesh/{id}`<br>`GET /openapi/v1/remesh/{id}/stream` | Refaz topologia, até 300k | 5 | [doc](https://docs.meshy.ai/api/remesh) |
| `POST /openapi/v1/convert`<br>`GET /openapi/v1/convert`<br>`GET /openapi/v1/convert/{id}`<br>`DELETE /openapi/v1/convert/{id}`<br>`GET /openapi/v1/convert/{id}/stream` | Exporta GLB, FBX, OBJ, USDZ, BLEND, STL, 3MF | 1 | [doc](https://docs.meshy.ai/api/convert) |
| `POST /openapi/v1/resize`<br>`GET /openapi/v1/resize`<br>`GET /openapi/v1/resize/{id}`<br>`DELETE /openapi/v1/resize/{id}`<br>`GET /openapi/v1/resize/{id}/stream` | Define altura ou maior lado em metros | 1 | [doc](https://docs.meshy.ai/api/resize) |
| `POST /openapi/v1/uv-unwrap`<br>`GET /openapi/v1/uv-unwrap`<br>`GET /openapi/v1/uv-unwrap/{id}`<br>`DELETE /openapi/v1/uv-unwrap/{id}`<br>`GET /openapi/v1/uv-unwrap/{id}/stream` | UV, até 40 mil faces | 5 | [doc](https://docs.meshy.ai/api/uv-unwrap) |
| `POST /openapi/v1/rigging`<br>`GET /openapi/v1/rigging`<br>`GET /openapi/v1/rigging/{id}`<br>`DELETE /openapi/v1/rigging/{id}`<br>`GET /openapi/v1/rigging/{id}/stream` | Rig automático | 5 | [doc](https://docs.meshy.ai/api/rigging) |
| `POST /openapi/v1/animations`<br>`GET /openapi/v1/animations`<br>`GET /openapi/v1/animations/{id}`<br>`DELETE /openapi/v1/animations/{id}`<br>`GET /openapi/v1/animations/{id}/stream` | Aplica animações | 3 por ação, até 10 | [doc](https://docs.meshy.ai/api/animation) |
| `POST /openapi/v1/text-to-image`<br>`GET /openapi/v1/text-to-image`<br>`GET /openapi/v1/text-to-image/{id}`<br>`DELETE /openapi/v1/text-to-image/{id}`<br>`GET /openapi/v1/text-to-image/{id}/stream` | Texto para imagem | 3 a 9, por modelo | [doc](https://docs.meshy.ai/api/text-to-image) |
| `POST /openapi/v1/image-to-image`<br>`GET /openapi/v1/image-to-image`<br>`GET /openapi/v1/image-to-image/{id}`<br>`DELETE /openapi/v1/image-to-image/{id}`<br>`GET /openapi/v1/image-to-image/{id}/stream` | Edição de imagem por prompt | 3 a 12, por modelo | [doc](https://docs.meshy.ai/api/image-to-image) |
| `POST /openapi/v1/print/multi-color`<br>`GET /openapi/v1/print/multi-color`<br>`GET /openapi/v1/print/multi-color/{id}`<br>`DELETE /openapi/v1/print/multi-color/{id}`<br>`GET /openapi/v1/print/multi-color/{id}/stream` | 3MF de 1 a 16 cores | 10 | [doc](https://docs.meshy.ai/api/multi-color-print) |
| `POST /openapi/v1/print/split`<br>`GET /openapi/v1/print/split`<br>`GET /openapi/v1/print/split/{id}`<br>`DELETE /openapi/v1/print/split/{id}`<br>`GET /openapi/v1/print/split/{id}/stream` | Divide em partes com conectores | 10 | [doc](https://docs.meshy.ai/api/auto-split) |
| `POST /openapi/v1/print/repair`<br>`GET /openapi/v1/print/repair`<br>`GET /openapi/v1/print/repair/{id}`<br>`DELETE /openapi/v1/print/repair/{id}`<br>`GET /openapi/v1/print/repair/{id}/stream` | Fecha a malha, engrossa paredes, remove texturas | 10 | [doc](https://docs.meshy.ai/api/repair-printability) |
| `POST /openapi/v1/print/analyze`<br>`GET /openapi/v1/print/analyze`<br>`GET /openapi/v1/print/analyze/{id}`<br>`DELETE /openapi/v1/print/analyze/{id}`<br>`GET /openapi/v1/print/analyze/{id}/stream` | Estanqueidade, volume, furos, paredes | Grátis | [doc](https://docs.meshy.ai/api/analyze-printability) |
| `POST /openapi/v1/text-to-motion`<br>`GET /openapi/v1/text-to-motion`<br>`GET /openapi/v1/text-to-motion/{id}`<br>`DELETE /openapi/v1/text-to-motion/{id}`<br>`GET /openapi/v1/text-to-motion/{id}/stream` | Texto para movimento; fora do OpenAPI | `prime` 10; `swift` 3 | [doc](https://docs.meshy.ai/api/text-to-motion) |
| `GET /openapi/v1/animations/library` | Catálogo de animações (operação única) | Grátis | [doc](https://docs.meshy.ai/api/animation-library) |
| `GET /openapi/v1/balance` | Saldo (operação única) | Grátis | [doc](https://docs.meshy.ai/api/balance) |
| `GET /openapi/v1/usage/tasks` | Exportação de uso, só Studio e Enterprise (operação única) | Grátis | [doc](https://docs.meshy.ai/api/usage) |

Contagem: 16 famílias no OpenAPI x 5 = 80, mais 3 operações únicas = **83**; Text to Motion soma 5 = **88**.

### Meshy Creative Lab: 85 operações, fora do OpenAPI

Oito produtos em dois estágios têm 10 operações cada, sob o prefixo indicado: `POST /prototype`; `POST /build`; `GET /prototype` e `GET /build`; `GET /prototype/:id` e `GET /build/:id`; `DELETE /prototype/:id` e `DELETE /build/:id`; `GET /prototype/:id/stream` e `GET /build/:id/stream`. Aqui `DELETE` cancela: reembolsa `PENDING`, cancela `IN_PROGRESS` sem reembolso e responde `400` em tarefa concluída ([Keychain](https://docs.meshy.ai/api/creative-lab-keychain)).

| Produto e doc | Prefixo | Operações | Custo: prototype, build | Saída |
|---|---|---|---|---|
| [Keychain](https://docs.meshy.ai/api/creative-lab-keychain) | `/openapi/creative-lab/keychain/v1` | 10 | 6, 30 | GLB, OBJ em zip, ou bundle |
| [Fridge Magnet](https://docs.meshy.ai/api/creative-lab-fridge-magnet) | `/openapi/creative-lab/fridge-magnet/v1` | 10 | 6, 30 | GLB, OBJ em zip, ou bundle |
| [Figure](https://docs.meshy.ai/api/creative-lab-figure) | `/openapi/creative-lab/figure/v1` | 10 | 6, 30 | GLB, OBJ, textura |
| [Vinyl Figure](https://docs.meshy.ai/api/creative-lab-vinyl-figure) | `/openapi/creative-lab/vinyl-figure/v1` | 10 | 6, 30 | GLB, OBJ, textura |
| [Brick Figure](https://docs.meshy.ai/api/creative-lab-brick-figure) | `/openapi/creative-lab/brick-figure/v1` | 10 | 6, 30 | GLB, OBJ, textura |
| [Lamp](https://docs.meshy.ai/api/creative-lab-lamp) | `/openapi/creative-lab/lamp/v1` | 10 | 30, 6 | STL da luminária e base, ou zip |
| [Keycap](https://docs.meshy.ai/api/creative-lab-keycap) | `/openapi/creative-lab/keycap/v1` | 10 | 12, 50 | GLB, OBJ em zip; mm reais |
| [Fidget Pixel](https://docs.meshy.ai/api/creative-lab-fidget-pixel) | `/openapi/creative-lab/fidget-pixel/v1` | 10 | 6, 30 | 3MF multicolor |
| [Collapsible Fidget](https://docs.meshy.ai/api/creative-lab-fidget-collapsible) (estágio único: `POST`, `GET` lista, `GET /:id`, `DELETE /:id`, `GET /:id/stream`) | `/openapi/creative-lab/fidget-collapsible/v1` | 5 | 6 | STL; GLB com preview |

Contagem: 8 x 10 + 5 = **85**. Total: 88 + 85 = **173 operações**, número calculado pelas notas e não publicado pela Meshy. Contando títulos de documentação o número é 141, ou 142 quando o `POST` de Text to 3D conta duas vezes (preview e refine). Os títulos por produto foram lidos diretamente em Keychain e Fidget Pixel; nos outros seis, o padrão foi confirmado por regex. O Creative Lab Figure é um produto de estilo chibi sem parâmetros de tamanho, portanto não substitui a figura personalizada de 4 a 15 cm sem teste.

### Meshy API v2: 28 rotas, status não declarado

**Nenhuma das duas páginas de migração declara status para a v2**; "preview" é **apenas uma inferência**. A base são nomes de componentes no JavaScript do site (`PreviewStrip`, flag `ApiV2`), e não um texto mostrado ao leitor. As páginas são `noindex`, não constam em `llms-full.txt` nem no OpenAPI, e não informam data de fim da v1 ([Migrate to API v2](https://docs.meshy.ai/en/api/migrate-to-v2); [docs chunk](https://docs.meshy.ai/_next/static/chunks/25kz956t9adt2.js)). Não se sabe quais contas podem chamá-la. Das 28 rotas, 5 de Text to 3D coincidem com as 173, de modo que a v2 acrescenta 23 caminhos novos (cálculo meu). Não há tabela de preços v2; os fatos declarados aparecem na coluna de custo ([v2 Migration Reference](https://docs.meshy.ai/en/api/migrate-to-v2/reference)).

**A. Literalmente documentadas nas páginas (13 com método, mais 1 sem método impresso)**

| Rota | Como aparece | Custo declarado |
|---|---|---|
| `GET /openapi/v2/tasks/{id}` | Método e caminho | Não declarado |
| `GET /openapi/v2/tasks?type=<type>` | Método e caminho | Não declarado |
| `GET /openapi/v2/tasks/{id}/stream` | Método e caminho | Não declarado |
| `DELETE /openapi/v2/tasks/{id}` | Método e caminho | Reembolsa `PENDING` |
| `POST /openapi/v2/image-to-3d` | Método e caminho | Não declarado; sem `target_formats`, só GLB |
| `POST /openapi/v2/text-to-3d` | Método e caminho | Uma chamada custa preview + refine |
| `GET /openapi/v2/usage/tasks` | Método e caminho | Não declarado |
| `POST /openapi/v2/multi-image-to-3d` | `curl -X POST` em aba oculta | Não declarado |
| `POST /openapi/v2/retexture` | `curl -X POST` em aba oculta | Não declarado |
| `POST /openapi/v2/remesh` | `curl -X POST` em aba oculta | 5; cadeia com resize e convert, 7 |
| `POST /openapi/v2/resize` | `curl -X POST` em aba oculta | 1 |
| `POST /openapi/v2/convert` | `curl -X POST` em aba oculta | 1 |
| `POST /openapi/v2/text-to-image` | `curl -X POST` em aba oculta | "Credits don't change" |
| `/openapi/v2/text-to-3d/{id}` | Caminho, descrito como leitura; método não impresso | Não declarado |

**B. Decorrem apenas da regra declarada (11), sem caminho impresso.** A regra diz: "Every /openapi/v1 endpoint that creates a task has a v2 version at the same path under /openapi/v2/, and so do Balance, Usage, and Animation Library."

| Rota derivada | Custo declarado |
|---|---|
| `POST /openapi/v2/image-to-image` | "Credits don't change" |
| `POST /openapi/v2/uv-unwrap` | Não declarado |
| `POST /openapi/v2/rigging` | Não declarado |
| `POST /openapi/v2/animations` | Não declarado |
| `POST /openapi/v2/text-to-motion` | Não declarado |
| `POST /openapi/v2/print/multi-color` | Não declarado |
| `POST /openapi/v2/print/analyze` | "is still free" |
| `POST /openapi/v2/print/repair` | Não declarado |
| `POST /openapi/v2/print/split` | Não declarado |
| `GET /openapi/v2/balance` | Não declarado |
| `GET /openapi/v2/animations/library` | Não declarado |

**C. Leituras próprias de Text to 3D (4), na forma do spec estável:** `GET /openapi/v2/text-to-3d`, `GET /openapi/v2/text-to-3d/{id}`, `DELETE /openapi/v2/text-to-3d/{id}`, `GET /openapi/v2/text-to-3d/{id}/stream`. A segunda é a rota sem método da tabela A, e a soma é 13 + 11 + 4 = 28. **Rotas que a referência diz não existirem:** leituras por endpoint, como `GET /openapi/v2/image-to-3d/{id}` (`404 route_not_found`), e qualquer Creative Lab em v2.

### Rotas não documentadas ou fora da API pública da Meshy

| Rota | Onde aparece | Situação |
|---|---|---|
| `GET /openapi/v1/showcases` | [meshy-cli](https://github.com/meshy-dev/meshy-cli) | Só em SDK; não documentada. "Enterprise tier; every request is billed" |
| `POST /openapi/v1/oauth/token` | [meshy-cli](https://github.com/meshy-dev/meshy-cli), [meshy-3d-agent](https://github.com/meshy-dev/meshy-3d-agent) | Só em SDK; não documentada |
| `POST /openapi/v1/oauth/device_authorization` | Mesmos repositórios | Só em SDK; não documentada |
| `/openapi/v1/text-to-texture` | `CHANGELOG.md` do [meshy-3d-agent](https://github.com/meshy-dev/meshy-3d-agent) | API aposentada em 2025-07-01 ([deprecations](https://docs.meshy.ai/api/deprecations)) |
| `/v2/text-to-3d` sem `/openapi` | [Deprecations](https://docs.meshy.ai/api/deprecations) | Alias obsoleto, sem data de remoção; documentado |
| `https://api.meshy.ai/web/public/animations/resources` | [Animation Library](https://docs.meshy.ai/api/animation-library) | Catálogo JSON público, não chamado |
| Endpoints "enterprise-only", superfície "d5", rotas em desenvolvimento | [OpenAPI](https://docs.meshy.ai/openapi.json), [site](https://www.meshy.ai/api) | Citados sem nomes; não documentados |

Webhooks da Meshy são criados só no painel; não há API de gestão nem criação em lote ([Webhooks](https://docs.meshy.ai/api/webhooks)). Text to Voxel foi aposentada. A chave de teste compartilhada foi aposentada em 2026-09-16, portanto não há sandbox ([changelog](https://docs.meshy.ai/api/changelog)). Campos só no OpenAPI, como `seed` e `negative_prompt` em Text to 3D, não têm garantia de comportamento.

## "100%" significa 100% do que os dois publicam, nunca do que os servidores aceitam

**Nenhum endpoint foi testado ao vivo, e nenhuma conta foi criada.** A ressalva é que, durante a auditoria, o auditor enviou duas requisições não autenticadas a hosts de API em busca de especificações, `https://api.tripo3d.ai/docs` e `https://api.meshy.ai/openapi.json`, ambas com 404, o que contraria a regra de consultar apenas documentação.

| Escopo | Veredito | Base | O que pode faltar |
|---|---|---|---|
| Páginas atuais da Tripo | **Verificado completo** neste snapshot | Router lista 44 públicas + 1 oculta; o resto retorna 404 | Páginas publicadas depois do bundle |
| Legado da Tripo (VitePress, 40 páginas; SPA, 24 módulos) | **Verificado completo** como índice | Mapas nos bundles | Parte listada não foi lida |
| Endpoints da Tripo | **Melhor esforço** | Regex nas páginas, dados do bundle, SDKs e CLI; não há OpenAPI | Rotas de servidor sem documentação |
| Páginas estáveis da Meshy | **Completo nas listadas** | Sitemap, `llms.txt` e rotas cruzados | Outras páginas com flag em chunks não baixados |
| Endpoints v1 da Meshy | **Verificado completo contra a documentação** | 83 operações do spec conferidas no texto; demais famílias confirmadas | Rotas fora da documentação, como `showcases` |
| API v2 da Meshy | **Melhor esforço** | Só duas páginas legíveis; URLs `/en/api/v2/*` redirecionam para v1 | Detalhe por endpoint e disponibilidade |

A profundidade de leitura variou. Na Tripo, as páginas de texto e multiview foram lidas por diff contra as de imagem; `sdk`, `cli`, `quick-start` e `authentication` foram lidas em parte; as respostas colapsadas da FAQ foram lidas pelo JavaScript do site em uma frente da pesquisa e ficaram ilegíveis em outra, e várias páginas legadas superadas não foram lidas. Na Meshy, oito páginas de Creative Lab foram lidas só até parâmetros e saídas, e guias e plugins do web app ficaram fora. As provas de SDK e CLI usam cópias da auditoria, de 2026-11-01, sem linha fixada. Não foi possível ler os textos dos banners `PreviewStrip` e `V1Strip`, o trust center da Meshy, nem os artigos de ajuda "Copyright Checklist for Meshy Reference Images and Assets" e "If I Cancel My Subscription, Will All My Models Revert to a CC-BY 4.0 License".

**Dois itens ficam em aberto.** O primeiro é a sua decisão: o pacote de migração da Meshy, [`meshy-v2-migration.zip`](https://docs.meshy.ai/downloads/meshy-v2-migration.zip) (200, `application/zip`, 101.438 bytes em consulta só de cabeçalho), foi **deliberadamente não baixado**, porque está fora das páginas designadas e a própria página pede que agentes de IA obtenham consentimento do usuário. Ele promete "every v1 to v2 mapping" e pode transformar as 11 rotas derivadas em literais. O segundo é o desligamento da V2 da Tripo, agendado para **2026-10-31** e **não verificado**; para a integração nova isso não muda nada, pois ela deve nascer na V3, mas qualquer código da Kubo que chame a V2 precisa ser revisado.

## Conclusão: cerca de US$ 28 em testes decidem o que a documentação não pode provar

A varredura muda a pergunta. O problema não é só escolher "o melhor gerador", porque o preço do modelo final é próximo nos dois (30 créditos em ambos, a valores de crédito diferentes): o que mais pesa é quem responde pelo arquivo que chega ao parceiro de impressão, e isso a Tripo não documenta em API. Outro achado é que a arquitetura atual, com preview e edição fora dos dois provedores, deixa de ser só economia e passa a reduzir a superfície contratual com Tripo e Meshy, ainda que transfira parte da pergunta para a Runware. O passo a seguir é barato e deve vir antes de qualquer integração completa: enviar as perguntas jurídicas e rodar os testes abaixo.

Orçamento estimado (cálculo meu): 10 imagens em duas configurações na Tripo, mais conversão, somam 800 créditos, ou US$ 8; na Meshy, os mesmos 10 casos com e sem Ultra, reparos, 5 Multi-Color, Resize e Convert somam cerca de 920 créditos, dentro do Pro de US$ 20; Trellis fica em US$ 0,10. **Use apenas imagens sem pessoas identificáveis e com direitos claros**, e créditos pagos na Tripo, para não violar a s. 2.2 nem cair na s. 5.2.1 durante os próprios testes. Impressões físicas não estão no orçamento.

| # | Teste | Decide | Critério de aprovação |
|---|---|---|---|
| 1 | Gerar 10 modelos na Tripo H3.1 com `face_limit` 300k e 1,2M, e na Meshy-7.1 com e sem `geometry_resolution` | Quem gera o final (requisitos 3, 6) | Contagem real de faces, detalhe visível em 4 e 15 cm; meça também a saída Meshy sem remesh |
| 2 | Passar todos por `print/analyze`, mais um validador independente | Se o reparo será exceção ou regra | Percentual com `is_watertight` verdadeiro; concordância entre validadores |
| 3 | Enviar GLB, FBX e STL da Tripo à Meshy por `model_url` em Analyze, Repair, Resize e Multi-Color | Viabilidade da mistura | Sem erro de entrada; textura aceita em `style: realistic`, que exige uma única textura base e UVs |
| 4 | Aplicar `flatten_bottom` e medir se Repair preserva a base plana | Ordem do pipeline | Base plana no fatiador, sem perda de altura visível |
| 5 | Dimensionar para 40 mm e 150 mm, depois abrir STL e 3MF no fatiador | Escala real (requisito 5c) | Erro dimensional dentro da tolerância dos parceiros; unidade confirmada |
| 6 | Imprimir 2 figuras por parceiro, de 4 e 15 cm, incluindo 1 multicolor com 3MF | Se o produto é vendável | Sem falha de parede, sem furo, aceitação do parceiro |
| 7 | Comparar preview Trellis e final Tripo da mesma imagem, e repetir `model_seed` com `face_limit` diferente | Risco de divergência para o cliente | Silhueta e identidade reconhecíveis; registrar se a malha muda |
| 8 | Consultar URL da Tripo em 60 s, 5 min e 24 h, e nova consulta da tarefa; conferir URL da Meshy | Conflito de validade (requisito 8) | Definir prazo de download; Celery baixa antes do menor prazo observado |
| 9 | Disparar webhook de cada provedor no Django, validar assinatura Tripo, simular duplicata e fora de ordem na Meshy; provocar 429 de concorrência | Desenho assíncrono | Tarefa idempotente, sem cobrança duplicada |
| 10 | Chamar `GET /openapi/v2/balance` com a chave da Meshy e consultar uma tarefa v1 em `GET /openapi/v2/tasks/{id}` | Se a v2 está aberta à conta | Resposta 200 ou recusa, para decidir a v1 ou v2 no adaptador |
| 11 | Só após resposta jurídica: fotos autorizadas de pessoas na Tripo | Moderação em fotos | Taxa de bloqueio por código `2008` ou `failed` |
