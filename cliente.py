import socket
import sys
import os

TAM_BUFFER = 4096
TAM_CABECALHO = 1024 

def iniciar_cliente(id_cliente, host, porta):
    # Mensagem exibida apenas uma vez ao iniciar, conforme exemplo do PDF
    print("Conexão criada com o servidor primário.") 

    while True:
        try:
            entrada = input("> ")
            if not entrada:
                continue
            
            partes = entrada.split()
            comando = partes[0].lower()

            if comando == 'exit':
                break

            # Conexão não-persistente (abre e fecha por comando), compatível com os logs do servidor no PDF
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_cliente:
                sock_cliente.connect((host, porta))

                if comando == 'upload':
                    if len(partes) != 2:
                        print("Uso: upload <caminho_do_arquivo>")
                        continue
                    
                    caminho_arquivo = partes[1]
                    if not os.path.exists(caminho_arquivo):
                        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
                        continue

                    nome_arquivo = os.path.basename(caminho_arquivo)
                    tamanho_arquivo = os.path.getsize(caminho_arquivo)
                    print(f"Enviando arquivo '{nome_arquivo}'...")

                    # Protocolo atualizado: id_cliente|upload|nome|tamanho
                    cabecalho_str = f"{id_cliente}|upload|{nome_arquivo}|{tamanho_arquivo}"
                    cabecalho = cabecalho_str.encode().ljust(TAM_CABECALHO)
                    sock_cliente.sendall(cabecalho)

                    with open(caminho_arquivo, 'rb') as f:
                        while True:
                            bloco = f.read(TAM_BUFFER)
                            if not bloco:
                                break
                            sock_cliente.sendall(bloco)
                    
                    resposta = sock_cliente.recv(TAM_BUFFER).decode()
                    print(resposta)

                elif comando == 'list':
                    # Protocolo atualizado: id_cliente|list
                    cabecalho_str = f"{id_cliente}|list"
                    cabecalho = cabecalho_str.encode().ljust(TAM_CABECALHO)
                    sock_cliente.sendall(cabecalho)
                    
                    resposta = sock_cliente.recv(TAM_BUFFER).decode()
                    print(resposta)
                
                else:
                    print(f"Comando '{comando}' desconhecido. Use: upload, list, exit.")

        except ConnectionRefusedError:
            print("Erro: A conexão foi recusada. O servidor primário está online?")
            break
        except Exception as e:
            print(f"Ocorreu um erro: {e}")
            break

if __name__ == "__main__":
    # Ajustado para receber o ID do cliente conforme enunciado
    if len(sys.argv) != 4:
        print(f"Uso correto: python3 {sys.argv[0]} <id_cliente> <host_servidor> <porta_servidor>")
        sys.exit(1)
    
    id_cliente = sys.argv[1]
    host_servidor = sys.argv[2]
    porta_servidor = int(sys.argv[3])
    
    iniciar_cliente(id_cliente, host_servidor, porta_servidor)