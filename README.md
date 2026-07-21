# Processo Seletivo – Intensivo Maker | IoT

## Relatório do Candidato
### Identificação do Candidato

- Matheus Henrique dos Santos Nonato
- GitHub: https://github.com/Henrique7613

---

## Visão Geral da Solução

Qual é o objetivo do seu projeto?
Contabilizar objetos em uma esteira de produção.

O que o sistema embarcado simulado faz?
Identificar, usando variações de luminosidade, a passagem de objetos, micro-paradas nas linhas de produção e o reset pós turno dos contadores.

Como o usuário interage com ele (se aplicável)?
Via terminal.

---

## Arquitetura do Sistema Embarcado

A arquitetura do projeto foi desenvolvida com base em um laço de repetição contínuo (polling), desenhado para ser ágil e não-bloqueante.

- Fluxo principal do programa: O código `main.py` roda dentro de um `while True`, lendo os estados do sensor analógico e do botão digital a cada ciclo (com um leve atraso de 10ms no final para estabilidade do simulador). A saída e comunicação com o usuário são feitas via impressão de mensagens no terminal (Serial Monitor).
- Temporização e Estrutura de Estados: Para evitar que o sistema ficasse travado (o que impediria a leitura do botão, por exemplo), o uso de `time.sleep()` foi descartado na lógica de tempo. Em vez disso, foi utilizada a função `time.ticks_ms()` para marcação de tempo assíncrona, comparando as diferenças (`time.ticks_diff()`).
- Interação de Componentes: O sistema interage capturando o sinal analógico do sensor LDR pelo pino 36 (ADC) e lendo o estado digital do botão pelo pino 18. O microcontrolador processa essas entradas, gerencia os estados lógicos (peça passando, bloqueada, reset) e reporta via terminal.

---

## Componentes Utilizados na Simulação

- Placa ESP32 (DevKit C V4): Microcontrolador principal responsável pela execução do código em MicroPython e pelo processamento das lógicas analógicas e digitais.
- Sensor Módulo Fotoresistor (LDR): Utilizado para simular a detecção da peça. A variação de luminosidade altera a tensão no pino AO (conectado ao pino analógico 36 do ESP32). Quando a luz diminui, simula a sombra de uma peça passando na esteira.
- Botão (Pushbutton): Conectado ao pino 18 com resistor interno de PULL-UP ativado. Atua como o comando de interface humana para zerar os contadores de peças no encerramento de um turno.

---

## Decisões Técnicas Relevantes

- Uso de Histerese na Leitura Analógica: Em vez de usar um único valor para identificar a peça, implementei uma janela de tolerância (histerese) com duas constantes (LIMIAR_BLOQUEADO = 15000 e LIMIAR_LIVRE = 40000). Isso previne ruídos de flutuação de luminosidade e impede "falsas contagens" quando a peça está nas bordas do sensor.
- Lógica de Detecção de Micro-parada: Ao iniciar o bloqueio de luz, o sistema salva o instante atual. Se o bloqueio se mantiver por mais de 5000 ms (5 segundos), o sistema dispara um único alerta de micro-parada sem travar o loop principal.
- Debounce por Software: O botão mecânico costuma gerar instabilidade ("bouncing") no sinal quando pressionado. Implementei um sistema de debounce lógico de 50ms (variável ATRASO_DEBOUNCE_MS), garantindo que apenas um pulso seja computado por clique e evitando que o contador resete múltiplas vezes ou falhe.

---

## Resultados Obtidos

- O que funciona corretamente: A contagem de objetos, a detecção de tempo excedido (micro-parada) e o reset do sistema via botão. Todos os requisitos principais de negócio foram atendidos com êxito.
- Resultado no Wokwi: O sistema monitora ativamente a variação da luz. Ao diminuir a luz do LDR no simulador (simulando a peça) e depois aumentar, o contador incrementa. Se a luz ficar baixa por mais de 5 segundos, o log de micro-parada é acionado. O clique no botão verde zera perfeitamente o contador para um novo ciclo de produção.

---

## Comentários Adicionais

- Desafios e Tempo: A maior dificuldade encontrada durante o teste foi o limite de tempo imposto. O prazo apertado tornou a etapa de conexões e o "wiring" lógico do simulador bastante desconfortáveis de executar com calma. A parte mecânica das ligações (como ajustar o JSON do diagrama) foi o maior ponto de atrito.
- Sobre o Problema: Achei os problemas propostos coerentes e de fácil compreensão técnica. A natureza do problema de automação de esteira é muito clara e a lógica necessária para encontrar as soluções foi rápida de mapear (conforme anexo de fluxo de pensamento utilizado).
- Limitações e Melhorias futuras: O código atual utiliza polling (leitura constante no loop while). Tendo mais tempo, a principal melhoria seria reestruturar a leitura do botão (e talvez a do sensor) para rodar via Interrupções de Hardware (IRQs). Isso otimizaria significativamente a eficiência de uso da CPU do ESP32.