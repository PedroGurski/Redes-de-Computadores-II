# Guia de Execução do Projeto de Redes

## Passo 1: Criar um arquivo de teste

Crie um arquivo para envio:

``` bash
echo "Este é um arquivo de teste para o trabalho de redes." > teste.txt
```

## Passo 2: Iniciar as 3 Réplicas

No mesmo diretório, abra 3 terminais e execute:

**Terminal 1**

``` bash
python3 replica.py 9000
```

**Terminal 2**

``` bash
python3 replica.py 9001
```

**Terminal 3**

``` bash
python3 replica.py 9002
```

Cada réplica ficará aguardando conexões.

## Passo 3: Iniciar o Servidor Primário

Abra outro terminal:

``` bash
python3 servidor.py 8500
```

## Passo 4: Executar o Cliente

No quinto terminal:

``` bash
python3 cliente.py 127.0.0.1 8500
```

O cliente mostrará um prompt:

    >

Agora você pode executar os comandos abaixo.

### Enviar arquivo

``` plaintext
> upload teste.txt
```

Você verá respostas no cliente, servidor primário e réplicas.

### Criar e enviar outro arquivo (opcional)

Crie outro arquivo:

``` bash
echo "Outro teste." > arquivo2.log
```

Envie:

``` plaintext
> upload arquivo2.log
```

### Listar arquivos no servidor

``` plaintext
> list
```

A saída esperada:

    teste.txt arquivo2.log

### Sair do cliente

``` plaintext
> exit
```
