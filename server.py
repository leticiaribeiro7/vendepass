import socket
import threading
import json
import time
import traceback
from enum import Enum

from user import User

users = []

lock = threading.Lock()

TIMEOUT = 120

class Menu(Enum):
    VER_ROTAS = 1
    COMPRAR_PASSAGEM = 2
    VER_PASSAGENS = 3
    CANCELAR_PASSAGEM = 4
    SAIR = 5

def main():
    
    with open('data.json', 'r') as file:
        rotas = json.load(file)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind(('0.0.0.0', 5555))   # colocar localhost em Windows
        server.listen()
        print("Servidor iniciado e aguardando conexões...")
    
    except Exception as e:
        return print(f'\n Não foi possível iniciar o servidor: {e}')
    
    while True:
        client, address = server.accept()
        print(f"Conexão estabelecida com {address}")

        thread = threading.Thread(target=handle_client, args=(client, rotas))
        thread.start()


def handle_client(client, rotas):
    client.settimeout(TIMEOUT)
    client.send(json.dumps({"message": "Digite seu nome"}).encode('utf-8'))
    name = json.loads(client.recv(2048).decode('utf-8').strip())

    user = get_or_create_user(name.get('option'))

    client.send(json.dumps({"message": f"Bem-vindo, {user.name}\n{menu()}"}).encode('utf-8'))

    while True:
        try:
            request = json.loads(client.recv(2048).decode('utf-8'))
            if not request:
                break
                
            # reseta o tempo a cada request
            client.settimeout(TIMEOUT)

            option = request.get('option')

            option_value = int(option)

            if option_value == Menu.VER_ROTAS.value:
                rotas_disponiveis = get_formatted_routes(rotas)
                client.send(json.dumps({"message": rotas_disponiveis}).encode('utf-8'))

            elif option_value == Menu.COMPRAR_PASSAGEM.value:
                rotas_disponiveis = get_formatted_routes(rotas)
                client.send(json.dumps({"message": f"{rotas_disponiveis}\nEscolha o número da rota correspondente:"}).encode('utf-8'))

                rota = json.loads(client.recv(2048).decode('utf-8').strip())
                id_rota = validate_int(rota.get('option'))

                # busca a rota na lista pelo id
                rota_selecionada = get_route(rotas, id_rota)
                comprar_passagem(rota_selecionada, client, user, rotas, menu)

            elif option_value == Menu.VER_PASSAGENS.value:
                if not user.passagens:
                    client.send(json.dumps({"message": f"Você não tem passagens compradas. \n{menu()}"}).encode('utf-8'))
                else:
                    passagens = get_formatted_tickets(user)
                    client.send(json.dumps({"message": passagens}).encode('utf-8'))

            elif option_value == Menu.CANCELAR_PASSAGEM.value:
                if not user.passagens:
                    client.send(json.dumps({"message": f"Você não tem passagens compradas. \n{menu()}"}).encode('utf-8'))
                else:
                    passagens = get_formatted_tickets(user)
                    client.send(json.dumps({"message": f"Suas passagens:\n{passagens}\nEscolha o número da passagem para cancelar: "}).encode('utf-8'))

                    num_passagem = json.loads(client.recv(2048).decode('utf-8').strip())
                    idx_passagem = validate_int(num_passagem.get('option')) - 1

                    if idx_passagem < len(user.passagens) and idx_passagem >= 0:
                        passagem_selecionada = user.get_passagem(idx_passagem)
                        cancelar_passagem(user, passagem_selecionada, rotas)

                        client.send(json.dumps({"message": f"Passagem cancelada com sucesso.\n{menu()}"}).encode('utf-8'))
                    else:
                        client.send(json.dumps({"message": "Passagem inválida."}).encode('utf-8'))

            elif option_value == Menu.SAIR.value:
                client.send(json.dumps({"status": "closed"}).encode('utf-8'))
                client.close()
                print(f"{user.name} se desconectou.")
                break

            else:
                client.send(json.dumps({"message": f"Opção inválida. Por favor, escolha uma opção do menu.\n{menu()}"}).encode('utf-8'))


        except socket.timeout:
            print(f"{user.name} desconectado por inatividade")
            client.send(json.dumps({"status":"timeout"}).encode('utf-8'))
            client.close()
            break
        except Exception as e:
            print(traceback.format_exc())
            client.close()
            break


def cancelar_passagem(user, passagem, rotas):
    user.passagens.remove(passagem)
    assento = passagem['assento']
    rota_cancelada = passagem['rota']

    rota = get_route(rotas, rota_cancelada['id'])

    if assento not in rota['assentos-livres']:
        rota['assentos-livres'].append(assento)
        rota['assentos-livres'].sort()

    # Atualiza as rotas afetadas
    for rota in rotas:
        
        # Se a rota cancelada é do tipo 'trecho', atualiza as rotas diretas correspondentes
        if rota_cancelada['tipo'] == 'trecho':
            for i in range(len(rota_cancelada['trechos']) - 1):
                origem_trecho = rota_cancelada['trechos'][i]
                destino_trecho = rota_cancelada['trechos'][i + 1]

                
                if rota['trechos'] == [origem_trecho, destino_trecho] and rota['tipo'] == 'direta':
                    if assento not in rota['assentos-livres']:
                        rota['assentos-livres'].append(assento)
                        rota['assentos-livres'].sort()
        
        # Se a rota cancelada é do tipo 'direta', atualiza as rotas de trechos correspondentes
        if rota_cancelada['tipo'] == 'direta':
            origem_trecho = rota_cancelada['trechos'][0]
            destino_trecho = rota_cancelada['trechos'][1]


            # verifica se a origem e destino da rota direta está contido na rota de trecho
            trecho_contido = origem_trecho in rota['trechos'] and destino_trecho in rota['trechos']

            # garante que os segmentos estão adjacentes no array de trechos
            if rota['tipo'] == 'trecho' and trecho_contido and rota['trechos'].index(destino_trecho) - rota['trechos'].index(origem_trecho) == 1:
                if assento not in rota['assentos-livres']:
                    rota['assentos-livres'].append(assento)
                    rota['assentos-livres'].sort()


def comprar_passagem(rota_selecionada, client, user, rotas, menu):
    # se o id enviado existir, continua o fluxo mandando escolher assento
    if rota_selecionada:

        if not rota_selecionada['assentos-livres']:
            client.send(json.dumps({"message" : f"Não há mais assentos disponíveis nesta rota. \n {menu()}"}).encode('utf-8'))

        else:
            assentos = get_formatted_assentos(rota_selecionada)
            client.send(json.dumps({"message" : f"Escolha o assento: {assentos}"}).encode('utf-8'))
            
            assento = json.loads(client.recv(2048).decode('utf-8').strip())

            numero_assento = validate_int(assento.get('option'))

            # lock ate finalizar a compra do assento
            lock.acquire()

            if numero_assento in rota_selecionada['assentos-livres']:
                reserva_efetuada = reserva_assento(rota_selecionada, numero_assento, rotas)

                # associa a passagem ao user respectivo
                if reserva_efetuada:
                    user.set_passagem({'rota': rota_selecionada, 'assento': numero_assento})
                    print(f"{user.name} comprou a passagem com os trechos {rota_selecionada['trechos']}")
                    client.send(json.dumps({"message" : f"Passagem comprada!\n {menu()}"}).encode('utf-8'))

            else: client.send(json.dumps({"message": "O assento não está disponível ou é inválido."}).encode('utf-8'))

            lock.release()

    else:
        client.send(json.dumps({"message": "Rota não encontrada ou inválida."}).encode('utf-8'))


def reserva_assento(rota_selecionada, numero_assento, rotas):
    
    if rota_selecionada['tipo'] == 'direta':
        rota_selecionada['assentos-livres'].remove(numero_assento)

        # bloqueia o assento nas rotas que tem trecho também
        for rota in rotas:
            for i in range(len(rota['trechos']) - 1):
                origem = rota['trechos'][i]
                destino = rota['trechos'][i + 1]
            
                if [origem, destino] == rota_selecionada['trechos']:
                    if numero_assento in rota['assentos-livres']:
                        rota['assentos-livres'].remove(numero_assento)

        return True
    
    elif rota_selecionada['tipo'] == 'trecho':
        rota_selecionada['assentos-livres'].remove(numero_assento)

        trechos_count = len(rota_selecionada['trechos'])

        # Itera por cada trecho da rota
        for i in range(trechos_count - 1):
            origem_trecho = rota_selecionada['trechos'][i]
            destino_trecho = rota_selecionada['trechos'][i + 1]

            # Bloqueia o assento nas rotas diretas correspondentes a cada trecho
            for rota in rotas:
                if rota['trechos'] == [origem_trecho, destino_trecho] and rota['tipo'] == 'direta':
                    if numero_assento in rota['assentos-livres']:
                        rota['assentos-livres'].remove(numero_assento)

        # Verifica se o assento foi bloqueado com sucesso na rota selecionada
        return numero_assento not in rota_selecionada['assentos-livres']
    return False


def get_formatted_routes(rotas):
    return "\n".join(
        f"{rota['id']}. {' -> '.join(rota['trechos'])} ({rota['tipo']})"
        for rota in rotas
    )

def get_formatted_tickets(user):
    return "\n".join(
            f"{i + 1}. Rota: {' -> '.join(passagem['rota']['trechos'])} - Assento: {passagem['assento']}"
            for i, passagem in enumerate(user.passagens)
        )

def get_formatted_assentos(rota):
    return ', '.join(str(assento) for assento in rota['assentos-livres'])


def get_or_create_user(name):
    for user in users:
        if name == user.name:
            return user

    user = User(name)
    users.append(user)
    return user

def get_route(rotas, id_rota):
    for rota in rotas:
        if rota['id'] == id_rota:
            return rota

def validate_int(user_input):
    if user_input.isdigit():
        return int(user_input)

    return 0


def menu():
    
    negrito = '\033[1m'
    padrao = '\033[0m'
    verde = '\033[0;32m'
    azul = '\033[0;36m'

    return (
        f'''\n 
        {azul}{negrito}
                VendePass
        {verde} 
        ==========================
        1. Ver rotas
        ==========================
        2. Comprar passagem
        ==========================
        3. Ver passagens compradas
        ==========================
        4. Cancelar passagem
        ==========================
        5. Sair
        ==========================
        Digite a opção desejada: 
        {padrao}'''
    )

if __name__ == "__main__":
    main()
