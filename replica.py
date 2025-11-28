# replica.py
import socket
import sys
import os

TAM_BUFFER = 4096  # 4KB

def iniciar_replica(porta):
    """Inicia um servidor réplica que ouve em uma porta específica."""
    
    # Cria um diretório para armazenar os arquivos desta réplica
    diretorio_replica = f"replica_{porta}_data"
    if not os.path.exists(diretorio_replica):
        os.makedirs(diretorio_replica)
    
    # Cria o socket TCP
    sock_replica = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_replica.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Associa o socket à porta
        sock_replica.bind(('', porta))
        sock_replica.listen(5)
        print(f"[RÉPLICA {porta}] Aguardando conexões na porta {porta}...")

        while True:
            # Aceita conexão do servidor primário
            conn, addr = sock_replica.accept()
            print(f"[RÉPLICA {porta}] Conexão recebida de {addr}")

            with conn:
                # 1. Recebe o cabeçalho (nome e tamanho do arquivo)
                cabecalho_bytes = conn.recv(TAM_BUFFER)
                cabecalho = cabecalho_bytes.decode()
                
                try:
                    nome_arquivo, tamanho_arquivo_str = cabecalho.split('|')
                    tamanho_arquivo = int(tamanho_arquivo_str)
                    print(f"[RÉPLICA {porta}] Recebendo arquivo '{nome_arquivo}' ({tamanho_arquivo} bytes)...")

                    # Caminho para salvar o arquivo
                    caminho_arquivo = os.path.join(diretorio_replica, nome_arquivo)

                    # 2. Recebe o conteúdo do arquivo em blocos
                    bytes_recebidos = 0
                    with open(caminho_arquivo, 'wb') as f:
                        while bytes_recebidos < tamanho_arquivo:
                            bloco = conn.recv(TAM_BUFFER)
                            if not bloco:
                                break
                            f.write(bloco)
                            bytes_recebidos += len(bloco)
                    
                    print(f"[RÉPLICA {porta}] Arquivo '{nome_arquivo}' armazenado com sucesso.")
                    
                    # 3. Envia confirmação de volta para o servidor primário
                    conn.sendall(b'OK')

                except (ValueError, IndexError) as e:
                    print(f"[RÉPLICA {porta}] Erro ao processar cabeçalho: {e}")
                    conn.sendall(b'ERRO')

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
