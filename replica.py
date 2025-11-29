import socket
import sys
import os

TAM_BUFFER = 4096
TAM_CABECALHO = 1024

def iniciar_replica(porta):
    diretorio_base_replica = f"replica_{porta}_data"
    if not os.path.exists(diretorio_base_replica):
        os.makedirs(diretorio_base_replica)
    
    sock_replica = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_replica.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock_replica.bind(('', porta))
        sock_replica.listen(5)
        print(f"[RÉPLICA {porta}] Aguardando conexões na porta {porta}...")

        while True:
            conn, addr = sock_replica.accept()
            with conn:
                cabecalho_bytes = conn.recv(TAM_CABECALHO)
                if not cabecalho_bytes:
                    continue
                
                cabecalho = cabecalho_bytes.decode().strip()
                
                try:
                    # Protocolo recebido do primario: id_cliente|nome_arquivo|tamanho
                    id_cliente, nome_arquivo, tamanho_str = cabecalho.split('|')
                    tamanho_arquivo = int(tamanho_str)
                    
                    # diretorio do cliente dentro da replica
                    dir_cliente = os.path.join(diretorio_base_replica, id_cliente)
                    if not os.path.exists(dir_cliente):
                        os.makedirs(dir_cliente)

                    caminho_arquivo = os.path.join(dir_cliente, nome_arquivo)
                    
                    print(f"[RÉPLICA {porta}] Recebendo '{nome_arquivo}' de Cliente {id_cliente}...")

                    bytes_recebidos = 0
                    with open(caminho_arquivo, 'wb') as f:
                        while bytes_recebidos < tamanho_arquivo:
                            restante = tamanho_arquivo - bytes_recebidos
                            tamanho = min(TAM_BUFFER, restante)
                            bloco = conn.recv(tamanho)
                            if not bloco:
                                break
                            f.write(bloco)
                            bytes_recebidos += len(bloco)
                    
                    if bytes_recebidos == tamanho_arquivo:
                        conn.sendall(b'OK')
                    else:
                        conn.sendall(b'ERRO_INCOMPLETO')

                except Exception as e:
                    print(f"[RÉPLICA {porta}] Erro: {e}")
                    conn.sendall(b'ERRO_GERAL')

    except Exception as e:
        print(f"Erro na replica {porta}: {e}")
    finally:
        sock_replica.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Uso correto: python3 {sys.argv[0]} <porta>")
        sys.exit(1)
    
    iniciar_replica(int(sys.argv[1]))