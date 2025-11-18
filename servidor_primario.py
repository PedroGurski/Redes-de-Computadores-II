import socket
import os
import sys
import threading
import glob

class ServidorPrimario:
    def __init__(self, porta):
        self.porta = porta
        self.host = 'localhost'
        self.replicas = [9000, 9001, 9002]  # Portas das réplicas
        self.diretorio_base = "diretorios/primario"
        self.criar_diretorio()
        
    def criar_diretorio(self):
        """Cria o diretório de armazenamento do servidor primário"""
        if not os.path.exists(self.diretorio_base):
            os.makedirs(self.diretorio_base)
            print(f"Diretório {self.diretorio_base} criado")
    
    def replicar_arquivo(self, cliente_id, nome_arquivo, caminho_arquivo):
        """Replica o arquivo para todas as réplicas"""
        print("Iniciando processo de replicação...")
        
        try:
            # Ler o arquivo
            with open(caminho_arquivo, 'rb') as arquivo:
                dados_arquivo = arquivo.read()
            
            tamanho_arquivo = len(dados_arquivo)
            confirmacoes = 0
            
            # Enviar para cada réplica
            for porta_replica in self.replicas:
                try:
                    sock_replica = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock_replica.settimeout(10)  # Timeout de 10 segundos
                    sock_replica.connect(('localhost', porta_replica))
                    
                    # Enviar informações do arquivo
                    info = f"{cliente_id}|{nome_arquivo}|{tamanho_arquivo}"
                    sock_replica.send(info.encode())
                    
                    # Aguardar confirmação para enviar dados
                    sock_replica.recv(1024)
                    
                    # Enviar dados do arquivo
                    sock_replica.sendall(dados_arquivo)
                    
                    # Aguardar confirmação final
                    resposta = sock_replica.recv(1024).decode()
                    if resposta == "OK":
                        print(f"[Réplica {porta_replica}] OK")
                        confirmacoes += 1
                    else:
                        print(f"[Réplica {porta_replica}] ERRO")
                    
                    sock_replica.close()
                    
                except Exception as e:
                    print(f"[Réplica {porta_replica}] Erro: {e}")
            
            return confirmacoes == len(self.replicas)
            
        except Exception as e:
            print(f"Erro durante replicação: {e}")
            return False
    
    def processar_cliente(self, conn, endereco, cliente_id):
        """Processa comandos de um cliente"""
        try:
            while True:
                # Receber comando do cliente
                comando = conn.recv(1024).decode().strip()
                if not comando:
                    break
                
                print(f"Conexão com cliente [{cliente_id}] estabelecida.")
                print(f"Operação solicitada: {comando.split()[0]}")
                
                if comando.startswith("upload"):
                    # Comando: upload <nome_arquivo>
                    partes = comando.split()
                    if len(partes) != 2:
                        conn.send(b"ERRO|Formato inválido. Use: upload <nome_arquivo>")
                        continue
                    
                    nome_arquivo = partes[1]
                    caminho_local = os.path.join(self.diretorio_base, nome_arquivo)
                    
                    # Receber informações do arquivo
                    info_data = conn.recv(1024).decode()
                    tamanho_arquivo = int(info_data)
                    
                    # Receber o arquivo
                    with open(caminho_local, 'wb') as arquivo:
                        bytes_recebidos = 0
                        while bytes_recebidos < tamanho_arquivo:
                            dados = conn.recv(4096)
                            if not dados:
                                break
                            arquivo.write(dados)
                            bytes_recebidos += len(dados)
                    
                    print(f"Arquivo '{nome_arquivo}' recebido. Armazenamento local concluído.")
                    
                    # Replicar para as réplicas
                    sucesso = self.replicar_arquivo(cliente_id, nome_arquivo, caminho_local)
                    
                    if sucesso:
                        conn.send(f"SUCESSO|Arquivo replicado com sucesso para {len(self.replicas)} servidores réplica.".encode())
                        print("Replicação concluída com sucesso. Enviando confirmação ao cliente.")
                    else:
                        conn.send(b"ERRO|Falha na replicação para uma ou mais réplicas")
                    
                elif comando == "list":
                    # Comando: list - listar arquivos
                    print("Recuperando listagem dos arquivos locais.")
                    arquivos = os.listdir(self.diretorio_base)
                    lista_arquivos = " ".join(arquivos) if arquivos else "Nenhum arquivo"
                    conn.send(lista_arquivos.encode())
                    print("Enviando informações ao cliente.")
                    
                elif comando == "quit":
                    break
                else:
                    conn.send(b"ERRO|Comando desconhecido")
                    
        except Exception as e:
            print(f"Erro ao processar cliente {cliente_id}: {e}")
        finally:
            conn.close()
            print(f"Conexão com cliente {cliente_id} fechada")
    
    def iniciar(self):
        """Inicia o servidor primário"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            sock.bind((self.host, self.porta))
            sock.listen(5)
            print(f"Servidor primário ouvindo na porta {self.porta}")
            
            contador_clientes = 0
            
            while True:
                conn, endereco = sock.accept()
                contador_clientes += 1
                print(f"Cliente {contador_clientes} conectado de {endereco}")
                
                # Criar thread para cada cliente
                thread = threading.Thread(target=self.processar_cliente, 
                                        args=(conn, endereco, contador_clientes))
                thread.daemon = True
                thread.start()
                
        except Exception as e:
            print(f"Erro no servidor primário: {e}")
        finally:
            sock.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python servidor_primario.py <porta>")
        sys.exit(1)
    
    porta = int(sys.argv[1])
    servidor = ServidorPrimario(porta)
    servidor.iniciar()