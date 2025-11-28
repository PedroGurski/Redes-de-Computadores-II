echo "Este é um arquivo de teste para o trabalho de redes." > teste.txt
Como Executar o Projeto
Para testar, você precisará de 5 terminais abertos no mesmo diretório onde salvou os arquivos .py.
Passo 1: Crie um arquivo de teste
No primeiro terminal, crie um arquivo para enviar.
Bash
echo "Este é um arquivo de teste para o trabalho de redes." > teste.txt
Passo 2: Inicie as 3 Réplicas
Terminal 1:
Bash
python3 replica.py 9000
Terminal 2:
Bash
python3 replica.py 9001
Terminal 3:
Bash
python3 replica.py 9002
Cada um deles exibirá uma mensagem "Aguardando conexões...".
Passo 3: Inicie o Servidor Primário
Terminal 4:
Bash
python3 servidor.py 8500
Ele também ficará aguardando conexões.
Passo 4: Execute o Cliente
Terminal 5:
Bash
python3 cliente.py 127.0.0.1 8500
O cliente se conectará e mostrará o prompt >. Agora você pode usar os comandos:
Faça o upload do arquivo:
Plain Text
> upload teste.txt
Você verá o feedback no cliente, no servidor primário e em todas as réplicas.
Crie e envie outro arquivo (opcional):
Bash
# No terminal do cliente, você pode sair do programa (Ctrl+C), criar outro arquivo e rodar de novo
echo "Outro teste." > arquivo2.log

# E no prompt do cliente:
> upload arquivo2.log
Liste os arquivos no servidor:
Plain Text
> list
A saída deverá ser teste.txt arquivo2.log.
Para sair:
Plain Text
> exit