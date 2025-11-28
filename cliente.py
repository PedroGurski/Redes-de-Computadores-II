# cliente.py
import socket
import sys
import os

TAM_BUFFER = 4096

def iniciar_cliente(host, porta):
    try:
        # Conecta ao servidor primário
        sock_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_cliente.connect((host, porta))
        print("Conexão criada com o servidor primário.")

        while True:
            # Lê comando do usuário
            entrada = input("> ")
            if not entrada:
                continue
            
            partes = entrada.split()
            comando = partes[0].lower()

            if comando == 'exit':
                break

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

                # 1. Envia o cabeçalho
                cabecalho = f"upload|{nome_arquivo}|{tamanho_arquivo}"
                sock_cliente.sendall(cabecalho.encode())

                # 2. Envia o conteúdo do arquivo
                with open(caminho_arquivo, 'rb') as f:
                    while True:
                        bloco = f.read(TAM_BUFFER)
                        if not bloco:
                            break
                        sock_cliente.sendall(bloco)
                
                # 3. Aguarda e imprime a resposta do servidor
                resposta = sock_cliente.recv(TAM_BUFFER).decode()
                print(resposta)

            elif comando == 'list':
                sock_cliente.sendall(b'list')
                resposta = sock_cliente.recv(TAM_BUFFER).decode()
                print(resposta)
            
            else:
                print(f"Comando '{comando}' desconhecido. Comandos disponíveis: upload, list, exit.")

    except ConnectionRefusedError:
        print("Erro: A conexão foi recusada. O servidor primário está online?")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        sock_cliente.close()
        print("Conexão encerrada.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Uso correto: python3 {sys.argv[0]} <host_servidor> <porta_servidor>")
        sys.exit(1)
    
    host_servidor = sys.argv[1]
    porta_servidor = int(sys.argv[2])
    iniciar_cliente(host_servidor, porta_servidor)
