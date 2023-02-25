import re
from easysnmp import snmp_walk
import json

##  Importar lista contendo os endereços ip's das impressoras
from ips_impressoras import lista_impressoras


#====================================================================
##  Criar listas vazias dos dados desejados e localização do arquivo json
lista_nomes = []
lista_modelos = []
lista_seriais = []
lista_ips = []
lista_status = []
sem_comunicacao = []


#====================================================================
##  Iniciar coleta e tratamento dos dados
for impressora in lista_impressoras:
    try:
        walk = snmp_walk(hostname=impressora, community='public', version=1)
        # 0 - Modelo
        # 3 - Não sei
        # 4 - Hostname
        # 10 - Rede
        # 122 - Endereço IP
        # 125 - Endereço de rede
        # 124 - Máscara de rede
        objetivo1 = walk[0]
        objetivo2 = walk[4]
        status = "online"

        objetivo1 = str(objetivo1)
        objetivo2 = str(objetivo2)

        alpha = re.findall("S/N.*' ", objetivo1)
        alpha = str(alpha[0]); serial = alpha.replace("' ", "").replace("S/N ", "")

        bravo = re.findall("'.*; ", objetivo1)
        bravo = str(bravo[0]); modelo = bravo.replace("; ", "").replace("'", "")

        charlie = re.findall("value='.*' ", objetivo2)
        charlie = str(charlie[0]); nome = charlie.replace("value='", "").replace("' ", "")
        

#====================================================================
##  Informações das impressoras desconectadas
    except:
        sem_comunicacao.append(impressora)
        serial = "nan"
        modelo = "nan"
        nome = "nan"
        status = "offline"

##  Inserir dados nas listas
    lista_ips.append(impressora)
    lista_seriais.append(serial)
    lista_modelos.append(modelo)
    lista_nomes.append(nome)
    lista_status.append(status)


#====================================================================
##  Inserir as listas dos dados em um dicionário e depois transforma-lo em dataframe
import pandas as pd

impressoras = {"nome": lista_nomes,
    "modelo": lista_modelos,
    "serie": lista_seriais,
    "ip": lista_ips,
    "status": lista_status
    }


#====================================================================
# Consultar os dados a partir do arquivo json;
def ler_json():
    
    global dados, item, chave, elemento
    with open ("impressoras.json") as arquivo:
        dados = json.load(arquivo)

        for chave in impressoras:
            item = 0

            for elemento in impressoras[chave]:
                try:
                    if dados[chave][item] == elemento:
                        alteracao = False
                    else:
                        print (f"Os valores para a chave [{chave}] são diferentes.")
                        print (dados[chave][item], elemento)
                        alteracao = True
                    # Reescrever o json apenas se houver alteração e se a informação não estiver vazia.
                    if alteracao is True and impressoras[chave][item] != "nan":
                        dados[chave][item] = impressoras[chave][item]
                    else:
                        pass
                    item += 1

                # Inserir dados de uma nova impressora
                except IndexError:
                    delta = dados[chave]
                    delta.append(elemento)


    exportar_json(dados)


#====================================================================
##  Função para exportar o dicionário para arquivo json
def exportar_json(x):
    with open ("impressoras.json", "w") as arquivo:
        json.dump (x, arquivo, indent = 4)


#====================================================================
try:
    ler_json()
except:
    print ("dados inseridos no json a partir do dicionário")
    exportar_json(impressoras)


df = pd.read_json("impressoras.json")
print ("\n\n", df)
