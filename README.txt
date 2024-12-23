Projeto desenvolvido na cadeira de Sistemas Operativos no 3º semestre da faculdade.
Consiste em um programa em python, invocado por um comando em shell, que procura a ocorrência de uma palavra dada em ficheiros dados.
O projeto foi feito para consolidar os conhecimentos adquiridos em assuntos como multiprocessamento/multithreading, sincronização e comunicação de processos, entre outros.

Possui 3 opções:
- l: retorna a quantidade de linhas com ocorrências da palavra.
- c: retorna a quantidade de ocorrências da palavra.
- i: retorna a quantidade de ocorrências da palavra em que aparece isoladamente.

--------------------------------------------------------
### Grupo: SO-TI-04
# Aluno 1: Libero Suprani 
# Aluno 2: Ravi Mughal 
# Aluno 3: Ricardo Avelãs 

--------------------------------------------------------
### Exemplos de comandos para executar o pwordcount:
1) ./pword -p 3 -w sistemas f1.txt 
2) ./pword -m l -w operativos f1.txt f2.txt
3) ./pword -m i -p 2 -w informatica f1.txt f2.txt
4) ./pword -m l -p 1 -i 5 -d logs.txt -w print f1.txt f2.txt f3.txt

Há também a opção -h, para ajuda.

--------------------------------------------------------
### Abordagem para a divisão dos ficheiros:
- Caso haja um ficheiro e mais de 1 processo, divide-se o conteúdo do ficheiro (por linha) entre os processos. É utilizada a função divide_content.

- Caso contrário, a função assign_files_to_processes cria uma lista de listas, em que a quantidade de listas internas é igual ao número de processos pretendidos 
e cada lista interna possui os ficheiros que serão analisados pelo processo filho n. 

Por ex: 3 processos e 4 ficheiros -> [[file1, file2], [file3], [file4]] -> neste caso, o processo filho 1 lidará com file1 e file2; o processo filho 2 lidará com file3; 
o processo filho 3 lidará com file4.

O critério para a divisão é o número de linhas em cada ficheiro.

--------------------------------------------------------
### Outras informações pertinentes:
- Adicionamos uma opção -h para ajuda no comando pword, que dá um exemplo de comando para executar o programa e informa sobre as flags.

- Para comunicação, foram utilizadas as classes Value e Array (memória partilhada) e Queue (troca de mensagens)
    - Utilizamos a função join_unclogging, que dá join nos processos chamando a função call_plummer, para que assim não haja deadlock
    quando os dados passados para a Queue shared_found sejam muito grandes e não haja um Queue.get() imediato. Ela coloca o que foi
    retornado da call_plummer na variável global unclogged_data.
   
    - A função call_plummer corre até que consiga fazer get dos dados presentes na Queue shared_found, retornando estes dados.

- Para a sincronização, utilizamos mutex.

- O timestamp utilizado para os logs foi: dd/mm/yy-hh/mm/ss
