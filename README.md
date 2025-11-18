

```
sistema_replicacao/
├── cliente.py
├── servidor_primario.py
├── replica.py
├── diretorios/
│   ├── primario/
│   ├── replica1/
│   ├── replica2/
│   └── replica3/
└── README.md
```


python executar_sistema.py

Método 2:
python replica.py 9000
python replica.py 9001
python replica.py 9002

python servidor_primario.py 8500
python cliente.py 1 localhost 8500


6. Funcionalidades Implementadas
✅ Upload de arquivos - Envio com replicação para 3 réplicas
✅ Listagem de arquivos - Recuperação da lista de arquivos armazenados
✅ Comunicação TCP - Usando sockets TCP
✅ Múltiplos clientes - Suporte a conexões concorrentes
✅ Diretórios separados - Armazenamento isolado para cada componente
✅ Confirmações - Feedback completo do processo de replicação

7. Características Técnicas
Threading: Processamento concorrente de múltiplos clientes
Buffer management: Envio de arquivos grandes em blocos de 4KB
Timeout handling: Timeouts para evitar travamentos
Error handling: Tratamento robusto de erros
Protocolo simples: Comunicação baseada em mensagens textuais e binárias


https://chat.deepseek.com/a/chat/s/f28792dc-12a9-459b-86f1-c98ccf08bc9f



OVERLEAF
https://overleaf.c3sl.ufpr.br/9865984233kycptnvpjwcm#4f5b20

# Redes-de-Computadores-II
