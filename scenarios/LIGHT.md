# Descritivo de Projeto: Contador de Produção Não-Intrusivo

Este documento apresenta a especificação técnica e o escopo de desenvolvimento para o projeto de um **Contador de Produção Não-Intrusivo**.

O objetivo é criar uma solução de baixo custo voltada para indústrias e linhas de montagem manuais ou semiautomáticas que operam sem Controladores Lógicos Programáveis (CLPs), eliminando a necessidade de anotações manuais e fornecendo métricas de produtividade em tempo real.

---

## 1. Visão Geral do Sistema

O sistema utiliza um sensor óptico baseado em fotorresistor (LDR) para monitorar a passagem de objetos (como caixas, embalagens ou peças) em uma esteira transportadora. Quando o feixe de luz é interrompido pelo objeto, o firmware registra o evento, atualiza o contador de produção, calcula o tempo de ciclo e monitora a ocorrência de micro-paradas na linha de produção. Um botão físico de reset permite ao operador encerrar e limpar o turno atual de trabalho.

---

## 2. Requisitos de Hardware (Arquitetura de Referência no Wokwi)

Para o desenvolvimento e simulação no ambiente Wokwi, os seguintes componentes e identificadores devem ser mapeados no arquivo `diagram.json`:

- **Microcontrolador:** ESP32 DevKit C v4 (ESP32 comum).

- **Sensor Óptico (LDR):** Mapeado com o ID `ldr1`, responsável por ler a variação de luminosidade em _lux_.

- **Botão de Reset:** Mapeado com o ID `btn1`, operando em modo Pull-Up ou Pull-Down externo/interno para o reset manual.

- **Interface de Comunicação:** Saída Serial (UART) para transmissão de logs e telemetria.

---

## 3. Arquitetura do Firmware e Lógica de Software

O código-fonte do firmware deve implementar as seguintes máquinas de estado e lógicas de controle:

### A. Inicialização do Sistema

Ao ser energizado, o microcontrolador deve configurar os pinos de entrada e saída, e imprimir obrigatoriamente a mensagem de inicialização no terminal serial.

- **Mensagem Esperada:** `"Contador de Producao Inicializado"`

### B. Lógica de Detecção e Contagem de Peças

- **Estado de Espera (Linha Livre):** O sensor `ldr1` lê valores altos de luminosidade (Ambiente iluminado, ex: > 500 lux).
- **Estado de Bloqueio (Peça Passando):** Quando um objeto obstrui a luz, o valor de lux cai abruptamente (ex: < 100 lux). O firmware deve detectar essa transição de descida.
- **Incremento:** A contagem só deve ser efetivada e incrementada quando a luz retornar ao estado normal (borda de subida), garantindo que a peça passou completamente pelo sensor.
- **Mensagem Serial Esperada:** `"Peca detectada! Total: X"` (onde X é o número acumulado).

### C. Lógica de Detecção de Micro-paradas

- O sistema deve rodar um temporizador não-bloqueante.
- Se o sensor `ldr1` permanecer no estado de bloqueio (lux baixo) por um tempo contínuo superior a um limiar parametrizado, o sistema deve entender que a esteira travou ou há um gargalo.
- **Mensagem Serial Esperada:** `"Alerta: Micro-parada detectada!"`

### D. Rotina de Reset de Turno

- A leitura do botão `btn1` deve conter um tratamento de _debounce_ para evitar falsos gatilhos.
- Ao detectar o acionamento estável do botão, as variáveis globais de contagem de peças e os cronômetros de produtividade devem ser zerados imediatamente.
- **Mensagem Serial Esperada:** `"Turno resetado com sucesso. Contadores zerados."`

---

## 4. Alinhamento com a Automação de Testes (CI)

Para garantir que o código desenvolvido esteja correto, o firmware deve responder estritamente aos estímulos configurados nos cenários do Wokwi CI. O código não deve conter funções bloqueantes longas em seu loop principal para que as validações de tempo funcionem perfeitamente. Mensagens com letras maiúsculas e minúsculas diferentes do específicado serão consideradas erradas.

### Parâmetros de Validação no CI

1. **Cenário de Contagem:** O teste injetará `lux: 800` -> `lux: 50` -> `lux: 800`. O log deve reportar o incremento com sucesso.
2. **Cenário de Parada:** O teste manterá `lux: 50` por mais de 5 segundos. O log deve exibir o alerta de micro-parada.
3. **Cenário de Reset:** O teste mudará o controle do botão para `pressed: 1` e depois `0`. O log deve confirmar o zeramento dos contadores.
