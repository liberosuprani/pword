### Grupo: SO-TI-04
# Aluno 1: Libero Suprani (fc62220)
# Aluno 2: Ravi Mughal (fc62504)
# Aluno 3: Ricardo Avelãs (fc62257)

# ex: ./pword -m c -p 1 -w exemplo ficheiro1.txt

import sys
from multiprocessing import Process

def divide_content(file: str, n_of_processes: int, word: str, mode: str):
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        n_of_lines = len(lines)
        division = n_of_lines // n_of_processes
        rest = n_of_lines % n_of_processes

        lines_per_process = [0 for i in range(n_of_processes)]
        
        pos = 0
        for i in range(0, n_of_lines, division):
            lines_per_process[pos] += division 
            if rest > 0:
                lines_per_process[pos] += 1
                rest -= 1
                
            pos += 1
            if pos == n_of_processes:
                pos = 0
                
        for i in range(n_of_processes):
            p = Process(target=find_word_in_text, args=(word, 
                                                        lines[0 if i == 0 else lines_per_process[i-1] : lines_per_process[i]], 
                                                        mode))
                    
        
'''
5 ficheiros, 3 processos 
f4 - 600 
f5 - 500
f1 - 100
f2 - 50
f3 - 50

p1 - [] 
p2 - []
p3 - []

p_aux_list = [ [(f4, 600),(f1, 100)], [(f4, 600),(f1, 100)] ]

{
    f1 : 100
    f2 : 50
    f3 : 50
    f4 : 600
    f5 : 500
}

ciclo:
    adiciona o maior (ainda não adicionado) no processo
    adiciona o proximo ficheiro no processo com menor valor
'''  

class FileObj:
    def __init__(self, name, size, index) -> None:
        self.name = name
        self.size = size
        self.index = index
    
   
def assign_files_to_processes(files: list, n_of_processes: int, word: str, mode: str):
    def sum_files_sizes(files_list: list):
        res = 0
        if len(files_list) == 0:
            return 0
        for f in files_list:
            res += f.size
        return res
    
    p_list = []

    if n_of_processes > len(files):
        n_of_processes = len(files)
    
    if n_of_processes == len(files):
        for i in range(n_of_processes):
            p = Process(target=find_word_in_file, args=(word, files[i], mode))
            p_list.append(p)
            p.start()
        for p in p_list:
            p.join()
    
    else:
        file_obj_list = []  
        for i, file in enumerate(files):
            with open(file, 'r', encoding="utf-8") as f:
                lines = f.readlines()
                file_obj_list.append(FileObj(name=file, size=len(lines)))

        file_obj_list.sort(key=lambda file_obj:file_obj.size, reverse=True)
        
        p_aux_list = [[] for i in range(n_of_processes)] # [[], [], []]
        
        for file_obj in file_obj_list: # 
            lowest_index = 0
            lowest_sum = sum_files_sizes(p_aux)
            
            for i, p_aux in enumerate(p_aux_list):
                if sum_files_sizes(p_aux) < lowest_sum:
                    lowest_sum = sum_files_sizes(p_aux)
                    lowest_index = i
            
            p_aux_list[lowest_index].append(file_obj)
            
        # [[f1.txt, f3.txt], [f2.txt], [f5.txt]]
        files_sub_list = [[f.name for f in p_aux] for p_aux in p_aux_list]
        
        for sub_list in files_sub_list:
            p = Process(target=find_word_in_file, args=(word, sub_list, mode))
            p_list.append(p)
            p.start()
        for p in p_list:
            p.join()
  
            
def find_word_in_text(word: str, text: str, mode):
    # TODO
    pass
  
def find_word_in_file(word: str, files: list, mode):
    # TODO
    pass
                 

            
        
def pword(args: list):
    mode = args[0]
    n_of_processes = int(args[1])
    word = args[2]
    files = args[3:]

    if len(files) == 1 and n_of_processes > 1: # 1 file and multiple processes
        divide_content(files[0], n_of_processes, word, mode)
    else:
        assign_files_to_processes(files, n_of_processes, word, mode)
            

def main(args):
    print('Programa: pword.py')
    print('Argumentos: ',args)
    
    pword(args)


if __name__ == "__main__":
    main(sys.argv[1:])
