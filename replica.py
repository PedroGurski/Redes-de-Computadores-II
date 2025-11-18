import socket
import os
import sys
import threading

class ReplicaServidor:
    def __init__(self, porta):
        self.porta = porta
        self.host = 'localhost'
        self.diretorio_base = f"diretorios/replica{porta-9000+1}"
        self.criar_diretorio()
        
    def criar_diretorio(self):
        """Cria o diretório de armazenamento da réplica"""
        if not os.path.exists(self.diretorio_base):
            os.makedirs(self.diretorio_base)
            print(f"Diretório {self.diretorio_base} criado")
    
    def processar_arquivo(self, conn, endereco):
        """Processa o recebimento de um arquivo"""
        try:
            # Receber informações do arquivo
            info_data = conn.recv(1024).decode()
            cliente_id, nome_arquivo, tamanho_arquivo = info_data.split('|')
            tamanho_arquivo = int(tamanho_arquivo)
            
            print(f"[Réplica {self.porta}] Recebendo arquivo '{nome_arquivo}' do cliente {cliente_id}")
            
            # Caminho completo do arquivo
            caminho_arquivo = os.path.join(self.diretorio_base, nome_arquivo)
            
            # Receber o arquivo em blocos
            with open(caminho_arquivo, 'wb') as arquivo:
                bytes_recebidos = 0
                while bytes_recebidos < tamanho_arquivo:
                    dados = conn.recv(4096)
                    if not dados:
                        break
                    arquivo.write(dados)
                    bytes_recebidos += len(dados)
            
            print(f"[Réplica {self.porta}] Arquivo '{nome_arquivo}' armazenado com sucesso")
            conn.send(b"OK")
            
        except Exception as e:
            print(f"[Réplica {self.porta}] Erro ao processar arquivo: {e}")
            conn.send(b"ERRO")
        finally:
            conn.close()
    
    def iniciar(self):
        """Inicia o servidor réplica"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            sock.bind((self.host, self.porta))
            sock.listen(5)
            print(f"Réplica ouvindo na porta {self.porta}")
            
            while True:
                conn, endereco = sock.accept()
                print(f"[Réplica {self.porta}] Conexão estabelecida com {endereco}")
                
                # Criar thread para processar cada conexão
                thread = threading.Thread(target=self.processar_arquivo, args=(conn, endereco))
                thread.daemon = True
                thread.start()
                
        except Exception as e:
            print(f"Erro na réplica: {e}")
        finally:
            sock.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python replica.py <porta>")
        sys.exit(1)
    
    porta = int(sys.argv[1])
    replica = ReplicaServidor(porta)
    replica.iniciar()