# Notas de revisión do borrador gold

## Base e criterio de selección

Esta referencia elaborouse exclusivamente a partir de `transcript.md` e `segments.json`. Revisei os 67 segmentos completos e comprobei que o texto e a etiqueta de voz de cada segmento coinciden nos dous ficheiros. Non consultei actas, web, outros documentos, configuracións, prompts nin execucións do pipeline.

Seleccionei exactamente 25 casos positivos, cada un cunha afirmación principal atómica. Prioricei importes, porcentaxes, períodos, resultados de votación, propostas e compromisos explícitos. As citas son fragmentos literais continuos; non se corrixiron vacilacións, cambios de lingua nin formas producidas polo ASR.

## Cobertura

Os positivos percorren toda a sesión: presentación inicial do orzamento (S0004-S0011), intervencións de oposición e propostas alternativas (S0015-S0036), resposta do goberno (S0041-S0057) e resultados formais ao final (S0064-S0066).

Por etiqueta de voz, a distribución é:

- `speaker_1`: 6 casos (G01-G06).
- `speaker_2`: 6 casos (G07-G12).
- `speaker_3`: 6 casos (G13-G18).
- `speaker_4`: 5 casos (G19-G23).
- `speaker_0`: 2 casos formais de presidencia e votación (G24-G25).

As etiquetas `speaker_*` son as da diarización e non se usaron para resolver identidades reais. S0025 anuncia a quenda do Grupo Popular, pero S0026-S0028 conservan `speaker_2`, a mesma etiqueta técnica da quenda anterior; a etiqueta só cambia a `speaker_3` en S0029, xa dentro da intervención anunciada. A referencia non usa S0026-S0028 como positivos e non intenta unificar etiquetas por grupo político ou persoa.

En modalidades hai 19 afirmacións presentadas como feitos, 3 propostas e 3 compromisos/anuncios de voto. Os casos G22 e G25 conservan por separado o anuncio previo de 19 votos e o resultado formal posterior, porque son actos discursivos distintos aínda que os números coincidan.

## Matices de aceptación

Os valores normalizados en `valueText` facilitan a comparación, pero a cita manda. Deben conservarse os límites e condicións expresos: «case» en G11; «ata» e «segundo os casos» en G13; «por debaixo do» e o terceiro trimestre en G15; e os períodos completos de G03, G06, G09 e G25. Un extractor non debería convertir importes propostos en aprobados, anuncios previos en resultados consumados nin incrementos en dotacións totais.

G16 conserva unha autocorrección representada na propia transcrición: primeiro aparecen 72 millóns e despois 72,3 millóns. O valor esperado toma a precisión final sen ocultar la secuencia literal. G21 deixa constancia de que a unidade monetaria está implícita, non pronunciada xunto a «dezaseis millóns».

## Limitacións e ambigüidades evitadas

Esta selección non é exhaustiva e non mide cobertura, precisión nin calidade global do futuro sistema. Está deseñada como un conxunto pequeno de exemplos inequívocos para revisión previa.

Non escoitei nin verifiquei o audio. Por iso, pasaxes con entidades pouco fiables, números difíciles de interpretar, autocorreccións inseguras ou frases truncadas quedaron fóra dos positivos e aparecen como controis negativos N02-N06. N01 controla ademais a atribución: unha cita reportada doutra persoa e doutro debate non debe converterse nun feito municipal en voz de `speaker_2`.

Non se comprobou a verdade no mundo das afirmacións políticas. O criterio é fidelidade á transcrición: quen di que, con que cifra, período, condición e modalidade. Tampouco se intentaron resolver contradicións entre participantes nin completar contexto ausente.

## Segunda revisión antes de conxelar

O asistente principal leu a transcrición completa e os 25 casos. Pediu substituír un caso ambiguo sobre «casi cien millones» que non explicitaba a natureza contable do importe. G20 agora recolle a comparación fiscal explícita de S0045. A referencia foi revisada antes de calquera petición a GLM.

Os campos `expectedMatter` son descricións de contexto para xulgar a pertenza, non nomes canónicos exactos que o modelo deba copiar. As partidas poden agruparse baixo o orzamento de Vigo de 2026 ou en asuntos específicos lexibles que manteñan ese contexto. Non hai unha anotación exhaustiva nin unha puntuación automática de granularidade do catálogo nesta primeira proba.
