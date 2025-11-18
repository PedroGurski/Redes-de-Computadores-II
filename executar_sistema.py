import subprocess
import time
import os
import signal
import sys

def criar_diretorios():
    """Cria os diretórios necessários"""
    diretorios = [
        "diretorios/primario",
        "diretorios/replica1", 
        "diretorios/replica2",
        "diretorios/replica3"
    ]
    
    for diretorio in diretorios:
        if not os.path.exists(diretorio):
            os.makedirs(diretorio)
            print(f"Diretório {diretorio} criado")

def executar_sistema():
    """Executa todo o sistema"""
    processos = []
    
    try:
        # Criar diretórios
        criar_diretorios()
        
        # Iniciar réplicas
        print("Iniciando réplicas...")
        for porta in [9000, 9001, 9002]:
            processo = subprocess.Popen([sys.executable, "replica.py", str(porta)])
            processos.append(processo)
            time.sleep(0.5)
        
        # Aguardar réplicas iniciarem
        time.sleep(2)
        
        # Iniciar servidor primário
        print("Iniciando servidor primário...")
        processo_primario = subprocess.Popen([sys.executable, "servidor_primario.py", "8500"])
        processos.append(processo_primario)
        
        # Aguardar servidor primário iniciar
        time.sleep(2)
        
        print("\nSistema iniciado!")
        print("Para executar o cliente, use: python cliente.py <id> localhost 8500")
        print("Exemplo: python cliente.py 1 localhost 8500")
        print("\nPressione Ctrl+C para encerrar o sistema")
        
        # Manter o script rodando
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nEncerrando sistema...")
        for processo in processos:
            processo.terminate()
        sys.exit(0)

if __name__ == "__main__":
    executar_sistema()