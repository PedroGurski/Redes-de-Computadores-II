import socket
import os
import sys

class Cliente:
    def __init__(self, cliente_id, host, porta):
        self.cliente_id = cliente_id
        self.host = host
        self.porta = porta
        self.socket = None
    
    def conectar(self):
        """Conecta ao servidor primário"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.porta))
            print("Conexão criada com o servidor primário.")
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False
    
    def enviar_arquivo(self, caminho_arquivo):
        """Envia um arquivo para o servidor primário"""
        if not os.path.exists(caminho_arquivo):
            print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado")
            return
        
        nome_arquivo = os.path.basename(caminho_arquivo)
        print(f"Enviando arquivo '{nome_arquivo}'...")
        
        try:
            # Enviar comando upload
            comando = f"upload {nome_arquivo}"
            self.socket.send(comando.encode())
            
            # Obter tamanho do arquivo
            tamanho_arquivo = os.path.getsize(caminho_arquivo)
            
            # Enviar tamanho do arquivo
            self.socket.send(str(tamanho_arquivo).encode())
            
            # Enviar arquivo em blocos
            with open(caminho_arquivo, 'rb') as arquivo:
                bytes_enviados = 0
                while bytes_enviados < tamanho_arquivo:
                    dados = arquivo.read(4096)
                    self.socket.sendall(dados)
                    bytes_enviados += len(dados)
            
            # Receber confirmação
            resposta = self.socket.recv(1024).decode()
            if resposta.startswith("SUCESSO"):
                print(resposta.split("|")[1])
            else:
                print(f"Erro: {resposta.split('|')[1]}")
                
        except Exception as e:
            print(f"Erro ao enviar arquivo: {e}")
    
    def listar_arquivos(self):
        """Solicita listagem de arquivos ao servidor"""
        try:
            self.socket.send(b"list")
            resposta = self.socket.recv(4096).decode()
            print(resposta)
        except Exception as e:
            print(f"Erro ao listar arquivos: {e}")
    
    def executar(self):
        """Loop principal do cliente"""
        if not self.conectar():
            return
        
        try:
            while True:
                comando = input("> ").strip()
                
                if comando.startswith("upload"):
                    partes = comando.split()
                    if len(partes) == 2:
                        self.enviar_arquivo(partes[1])
                    else:
                        print("Uso: upload <caminho_arquivo>")
                
                elif comando == "list":
                    self.listar_arquivos()
                
                elif comando == "quit":
                    self.socket.send(b"quit")
                    break
                
                else:
                    print("Comandos disponíveis: upload <arquivo>, list, quit")
                    
        except KeyboardInterrupt:
            print("\nCliente encerrado")
        except Exception as e:
            print(f"Erro: {e}")
        finally:
            if self.socket:
                self.socket.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python cliente.py <cliente_id> <host> <porta>")
        sys.exit(1)
    
    cliente_id = sys.argv[1]
    host = sys.argv[2]
    porta = int(sys.argv[3])
    
    cliente = Cliente(cliente_id, host, porta)
    cliente.executar()