# servidor.py
import socket
import sys
import os
import threading

TAM_BUFFER = 4096
REPLICAS = [('127.0.0.1', 9000), ('127.0.0.1', 9001), ('127.0.0.1', 9002)] # Endereços das réplicas
DIRETORIO_PRIMARIO = "servidor_primario_data"

def replicar_para_servidores(nome_arquivo, caminho_completo):
    """Conecta-se a cada réplica e envia o arquivo."""
    tamanho_arquivo = os.path.getsize(caminho_completo)
    cabecalho = f"{nome_arquivo}|{tamanho_arquivo}".encode()
    
    confirmacoes = 0
    total_replicas = len(REPLICAS)

    for i, (host_replica, porta_replica) in enumerate(REPLICAS, 1):
        try:
            sock_replica = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_replica.connect((host_replica, porta_replica))
            
            # Envia cabeçalho e arquivo
            sock_replica.sendall(cabecalho)
            with open(caminho_completo, 'rb') as f:
                while True:
                    bloco = f.read(TAM_BUFFER)
                    if not bloco:
                        break
                    sock_replica.sendall(bloco)
            
            # Aguarda confirmação
            resposta = sock_replica.recv(1024).decode()
            if resposta == 'OK':
                print(f"[Réplica {i}] OK")
                confirmacoes += 1
            else:
                print(f"[Réplica {i}] Falhou")

            sock_replica.close()
        except Exception as e:
            print(f"[Réplica {i}] Falha na conexão: {e}")

    return confirmacoes == total_replicas

def lidar_com_cliente(conn, addr):
    """Função executada em uma thread para cada cliente conectado."""
    print(f"Conexão com cliente {addr} estabelecida.")
    
    try:
        with conn:
            while True:
                # Recebe o comando do cliente
                comando_raw = conn.recv(TAM_BUFFER)
                if not comando_raw:
                    break # Conexão fechada pelo cliente
                
                comando_str = comando_raw.decode().strip()
                partes = comando_str.split('|')
                operacao = partes[0]

                print(f"Operação solicitada: {operacao}")

                if operacao == 'upload':
                    nome_arquivo = partes[1]
                    tamanho_arquivo = int(partes[2])
                    
                    print(f"Arquivo '{nome_arquivo}' recebido. Armazenamento local concluído.")
                    caminho_arquivo = os.path.join(DIRETORIO_PRIMARIO, nome_arquivo)

                    # Recebe e salva o arquivo localmente
                    bytes_recebidos = 0
                    with open(caminho_arquivo, 'wb') as f:
                        while bytes_recebidos < tamanho_arquivo:
                            bloco = conn.recv(TAM_BUFFER)
                            if not bloco:
                                break
                            f.write(bloco)
                            bytes_recebidos += len(bloco)
                    
                    # Inicia processo de replicação
                    print("Iniciando processo de replicação...")
                    sucesso_replicacao = replicar_para_servidores(nome_arquivo, caminho_arquivo)

                    if sucesso_replicacao:
                        print("Replicação concluída com sucesso. Enviando confirmação ao cliente.")
                        msg = f"Envio concluído. Arquivo replicado com sucesso para {len(REPLICAS)} servidores réplica."
                        conn.sendall(msg.encode())
                    else:
                        print("Falha na replicação. Informando cliente.")
                        conn.sendall(b"Erro: Falha ao replicar o arquivo para todos os servidores.")

                elif operacao == 'list':
                    print("Recuperando listagem dos arquivos locais.")
                    try:
                        arquivos = os.listdir(DIRETORIO_PRIMARIO)
                        lista_arquivos = " ".join(arquivos) if arquivos else "Nenhum arquivo no servidor."
                        conn.sendall(lista_arquivos.encode())
                        print("Enviando informações ao cliente.")
                    except FileNotFoundError:
                        conn.sendall(b"Nenhum arquivo no servidor.")

    except ConnectionResetError:
        print(f"Conexão com {addr} foi resetada pelo cliente.")
    except Exception as e:
        print(f"Erro na conexão com {addr}: {e}")
    finally:
        print(f"Conexão com cliente {addr} encerrada.\n")


def iniciar_servidor_primario(porta):
    if not os.path.exists(DIRETORIO_PRIMARIO):
        os.makedirs(DIRETORIO_PRIMARIO)

    sock_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_servidor.bind(('', porta))
    sock_servidor.listen(5)
    print(f"[SERVIDOR] Aguardando conexões na porta {porta}...")

    while True:
        conn, addr = sock_servidor.accept()
        # Cria uma nova thread para cada cliente
        thread_cliente = threading.Thread(target=lidar_com_cliente, args=(conn, addr))
        thread_cliente.start()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Uso correto: python3 {sys.argv[0]} <porta>")
        sys.exit(1)
    
    porta_servidor = int(sys.argv[1])
    iniciar_servidor_primario(porta_servidor)
