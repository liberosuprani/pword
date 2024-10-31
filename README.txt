### Grupo: SO-TI-04
# Aluno 1: Libero Suprani (fc62220)
# Aluno 2: Ravi Mughal (fc62504)
# Aluno 3: Ricardo Avelãs (fc62257)

--------------------------------------------------------
### Exemplos de comandos para executar o pwordcount:
1) ./pword -m c -p 3 -w sistemas f1.txt 
2) ./pword -m l -w operativos f1.txt f2.txt
3) ./pword -m i -p 2 -w informatica f1.txt f2.txt

--------------------------------------------------------
### Limitações da implementação:
- Não há nenhuma limitação de nosso conhecimento

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
- ...
