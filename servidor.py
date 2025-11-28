# servidor.py (CORRIGIDO)
import socket
import sys
import os
import threading

TAM_BUFFER = 4096
TAM_CABECALHO = 1024 # Mesmo tamanho fixo
REPLICAS = [('127.0.0.1', 9000), ('127.0.0.1', 9001), ('127.0.0.1', 9002)]
DIRETORIO_PRIMARIO = "servidor_primario_data"

def replicar_para_servidores(nome_arquivo, caminho_completo):
    tamanho_arquivo = os.path.getsize(caminho_completo)
    
    # Cria e preenche o cabeçalho para ter um tamanho fixo
    cabecalho_str = f"{nome_arquivo}|{tamanho_arquivo}"
    cabecalho = cabecalho_str.encode().ljust(TAM_CABECALHO)
    
    confirmacoes = 0
    total_replicas = len(REPLICAS)

    for i, (host_replica, porta_replica) in enumerate(REPLICAS, 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_replica:
                sock_replica.connect((host_replica, porta_replica))
                
                # Envia cabeçalho de tamanho fixo
                sock_replica.sendall(cabecalho)
                
                # Envia conteúdo do arquivo
                with open(caminho_completo, 'rb') as f:
                    while True:
                        bloco = f.read(TAM_BUFFER)
                        if not bloco:
                            break
                        sock_replica.sendall(bloco)
                
                resposta = sock_replica.recv(1024).decode()
                if resposta == 'OK':
                    print(f"[Réplica {i}] OK")
                    confirmacoes += 1
                else:
                    print(f"[Réplica {i}] Falhou com resposta: {resposta}")
        except Exception as e:
            print(f"[Réplica {i}] Falha na conexão: {e}")

    return confirmacoes == total_replicas

def lidar_com_cliente(conn, addr):
    print(f"Conexão com cliente {addr} estabelecida.")
    try:
        with conn:
            # 1. Recebe o cabeçalho de tamanho fixo do cliente
            cabecalho_bytes = conn.recv(TAM_CABECALHO)
            if not cabecalho_bytes:
                return
            
            comando_str = cabecalho_bytes.decode().strip()
            partes = comando_str.split('|')
            operacao = partes[0]

            print(f"Operação solicitada: {operacao}")

            if operacao == 'upload':
                nome_arquivo = partes[1]
                tamanho_arquivo = int(partes[2])
                
                caminho_arquivo = os.path.join(DIRETORIO_PRIMARIO, nome_arquivo)

                # 2. Recebe e salva o arquivo localmente
                bytes_recebidos = 0
                with open(caminho_arquivo, 'wb') as f:
                    while bytes_recebidos < tamanho_arquivo:
                        restante = tamanho_arquivo - bytes_recebidos
                        tamanho_leitura = min(TAM_BUFFER, restante)
                        bloco = conn.recv(tamanho_leitura)
                        if not bloco:
                            break
                        f.write(bloco)
                        bytes_recebidos += len(bloco)
                
                print(f"Arquivo '{nome_arquivo}' recebido. Armazenamento local concluído.")
                
                print("Iniciando processo de replicação...")
                sucesso_replicacao = replicar_para_servidores(nome_arquivo, caminho_arquivo)

                if sucesso_replicacao:
                    msg = f"Envio concluído. Arquivo replicado com sucesso para {len(REPLICAS)} servidores réplica."
                    conn.sendall(msg.encode())
                else:
                    conn.sendall(b"Erro: Falha ao replicar o arquivo para todos os servidores.")

            elif operacao == 'list':
                print("Recuperando listagem dos arquivos locais.")
                try:
                    arquivos = os.listdir(DIRETORIO_PRIMARIO)
                    lista_arquivos = " ".join(arquivos) if arquivos else "Nenhum arquivo no servidor."
                    conn.sendall(lista_arquivos.encode())
                except FileNotFoundError:
                    conn.sendall(b"Nenhum arquivo no servidor.")
    except (ConnectionResetError, BrokenPipeError):
        print(f"Conexão com {addr} foi encerrada abruptamente.")
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
        thread_cliente = threading.Thread(target=lidar_com_cliente, args=(conn, addr))
        thread_cliente.start()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Uso correto: python3 {sys.argv[0]} <porta>")
        sys.exit(1)
    
    porta_servidor = int(sys.argv[1])
    iniciar_servidor_primario(porta_servidor)
