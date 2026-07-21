import machine
import time

sensorzin = machine.ADC(machine.Pin(36))
sensorzin.atten(machine.ADC.ATTN_11DB)

butanzin = machine.Pin(18, machine.Pin.IN, machine.Pin.PULL_UP)

contador_pecas = 0
peca_passando = False
tempo_bloqueio_inicio = 0
micro_parada_alertada = False

LIMIAR_BLOQUEADO = 15000
LIMIAR_LIVRE = 40000

TEMPO_MICRO_PARADA_MS = 7000    

estadoAnteriorButanzin = 1
butanzinPressionadoAviso = False
ultimo_tempo_debounce = 0
ATRASO_DEBOUNCE_MS = 50

print("Contador de Producao Inicializado")

while True:
    tempo_atual = time.ticks_ms()

    leitura_sensorzin = sensorzin.read_u16()
    
    if not peca_passando and leitura_sensorzin < LIMIAR_BLOQUEADO:
        peca_passando = True
        tempo_bloqueio_inicio = tempo_atual
        micro_parada_alertada = False

    elif peca_passando and leitura_sensorzin > LIMIAR_LIVRE:
        peca_passando = False
        contador_pecas += 1
        print(f"Peca detectada! Total: {contador_pecas}")

    if peca_passando and not micro_parada_alertada:
        if time.ticks_diff(tempo_atual, tempo_bloqueio_inicio) > TEMPO_MICRO_PARADA_MS:
            print("Alerta: Micro-parada detectada!")
            micro_parada_alertada = True

    leitura_butanzin = butanzin.value()

    if leitura_butanzin != estadoAnteriorButanzin:
        ultimo_tempo_debounce = tempo_atual

    if time.ticks_diff(tempo_atual, ultimo_tempo_debounce) > ATRASO_DEBOUNCE_MS:
        if leitura_butanzin == 0 and not butanzinPressionadoAviso:
            contador_pecas = 0
            print("Turno resetado com sucesso. Contadores zerados.")
            butanzinPressionadoAviso = True
            
        elif leitura_butanzin == 1:
            butanzinPressionadoAviso = False

    estadoAnteriorButanzin = leitura_butanzin

    time.sleep_ms(10)