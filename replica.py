# replica.py (CORRIGIDO)
import socket
import sys
import os

TAM_BUFFER = 4096
TAM_CABECALHO = 1024 # Tamanho fixo para o cabeçalho

def iniciar_replica(porta):
    diretorio_replica = f"replica_{porta}_data"
    if not os.path.exists(diretorio_replica):
        os.makedirs(diretorio_replica)
    
    sock_replica = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_replica.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock_replica.bind(('', porta))
        sock_replica.listen(5)
        print(f"[RÉPLICA {porta}] Aguardando conexões na porta {porta}...")

        while True:
            conn, addr = sock_replica.accept()
            print(f"[RÉPLICA {porta}] Conexão recebida de {addr}")

            with conn:
                # 1. Recebe o cabeçalho de tamanho fixo
                cabecalho_bytes = conn.recv(TAM_CABECALHO)
                if not cabecalho_bytes:
                    continue
                
                # Remove o preenchimento e decodifica
                cabecalho = cabecalho_bytes.decode().strip()
                
                try:
                    nome_arquivo, tamanho_arquivo_str = cabecalho.split('|')
                    tamanho_arquivo = int(tamanho_arquivo_str)
                    print(f"[RÉPLICA {porta}] Recebendo arquivo '{nome_arquivo}' ({tamanho_arquivo} bytes)...")

                    caminho_arquivo = os.path.join(diretorio_replica, nome_arquivo)

                    # 2. Recebe o conteúdo do arquivo
                    bytes_recebidos = 0
                    with open(caminho_arquivo, 'wb') as f:
                        while bytes_recebidos < tamanho_arquivo:
                            # Calcula quanto ainda falta receber para não ler além do necessário
                            restante = tamanho_arquivo - bytes_recebidos
                            tamanho_leitura = min(TAM_BUFFER, restante)
                            bloco = conn.recv(tamanho_leitura)
                            if not bloco:
                                break
                            f.write(bloco)
                            bytes_recebidos += len(bloco)
                    
                    if bytes_recebidos == tamanho_arquivo:
                        print(f"[RÉPLICA {porta}] Arquivo '{nome_arquivo}' armazenado com sucesso.")
                        conn.sendall(b'OK')
                    else:
                        print(f"[RÉPLICA {porta}] Erro: recepção incompleta.")
                        conn.sendall(b'ERRO_INCOMPLETO')

                except (ValueError, IndexError) as e:
                    print(f"[RÉPLICA {porta}] Erro ao processar cabeçalho: {e}")
                    conn.sendall(b'ERRO_CABECALHO')

    except Exception as e:
        print(f"[RÉPLICA {porta}] Erro fatal: {e}")
    finally:
        sock_replica.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Uso correto: python3 {sys.argv[0]} <porta>")
        sys.exit(1)
    
    porta_replica = int(sys.argv[1])
    iniciar_replica(porta_replica)
