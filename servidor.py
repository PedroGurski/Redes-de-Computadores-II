import socket
import sys
import os
import threading

TAM_BUFFER = 4096
TAM_FILA = 5
TAM_CABECALHO = 1024

# Caso tenha mais replicas, adicionamos manualmente
REPLICAS = [('127.0.0.1', 9000), ('127.0.0.1', 9001), ('127.0.0.1', 9002)]
DIRETORIO_PRIMARIO = "servidor_primario_data"

def replicar_para_servidores(id_cliente, nome_arquivo, caminho_completo):
    tamanho_arquivo = os.path.getsize(caminho_completo)
    
    # protocolo: id|nome|tamanho
    cabecalho_str = f"{id_cliente}|{nome_arquivo}|{tamanho_arquivo}"
    cabecalho = cabecalho_str.encode().ljust(TAM_CABECALHO)
    
    confirmacoes = 0
    total_replicas = len(REPLICAS)

    for i, (host_replica, porta_replica) in enumerate(REPLICAS, 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock_replica:
                sock_replica.connect((host_replica, porta_replica))
                sock_replica.sendall(cabecalho)
                
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
                    print(f"[Réplica {i}] Falhou: {resposta}")
        except Exception as e:
            print(f"[Réplica {i}] Falha na conexão: {e}")

    return confirmacoes == total_replicas

def lidar_com_cliente(conn, addr):
    try:
        with conn:
            cabecalho_bytes = conn.recv(TAM_CABECALHO)
            if not cabecalho_bytes:
                return
            
            comando_str = cabecalho_bytes.decode().strip()
            partes = comando_str.split('|')
            
            # Protocolo: id_cliente|operacao|
            if len(partes) < 2:
                return

            id_cliente = partes[0]
            operacao = partes[1]

            print(f"Conexão com cliente [{id_cliente}] estabelecida.")
            print(f"Operação solicitada: {operacao}")

            # diretorio do cliente
            dir_cliente = os.path.join(DIRETORIO_PRIMARIO, id_cliente)
            if not os.path.exists(dir_cliente):
                os.makedirs(dir_cliente)

            if operacao == 'upload':
                nome_arquivo = partes[2]
                tamanho_arquivo = int(partes[3])
                
                caminho_arquivo = os.path.join(dir_cliente, nome_arquivo)

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
                
                # Passa o ID para as rweplicas tambem
                sucesso = replicar_para_servidores(id_cliente, nome_arquivo, caminho_arquivo)

                if sucesso:
                    print("Replicação concluída com sucesso. Enviando confirmação ao cliente.\n")
                    msg = f"Envio concluído. Arquivo replicado com sucesso para {len(REPLICAS)} servidores réplica."
                    conn.sendall(msg.encode())
                else:
                    conn.sendall(b"Erro na replicacao.")

            elif operacao == 'list':
                print("Recuperando listagem dos arquivos locais.")
                try:
                    # lista somente os arquivos do cliente especifico | fizemos assim pois ficamos em dúvida se era para retornar todos os arquivos que foram armazenados
                    arquivos = os.listdir(dir_cliente)
                    lista_arquivos = " ".join(arquivos) if arquivos else ""
                    print("Enviando informações ao cliente.\n")
                    conn.sendall(lista_arquivos.encode())
                except FileNotFoundError:
                    conn.sendall(b"")
                    
    except Exception as e:
        print(f"Erro na conexão: {e}")
    finally:
        pass 

def iniciar_servidor_primario(porta):
    if not os.path.exists(DIRETORIO_PRIMARIO):
        os.makedirs(DIRETORIO_PRIMARIO)

    sock_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock_servidor.bind(('', porta))
    sock_servidor.listen(TAM_FILA)
    print(f"[SERVIDOR] Aguardando conexões na porta {porta}...")

    while True:
        conn, addr = sock_servidor.accept()
        t = threading.Thread(target=lidar_com_cliente, args=(conn, addr))
        t.start()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Uso correto: python3 {sys.argv[0]} <porta>")
        sys.exit(1)
    
    iniciar_servidor_primario(int(sys.argv[1]))