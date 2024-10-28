### Grupo: SO-TI-04
# Aluno 1: Libero Suprani (fc62220)
# Aluno 2: Ravi Mughal (fc62504)
# Aluno 3: Ricardo Avelãs (fc62257)

# ex: ./pword -m c -p 1 -w exemplo ficheiro1.txt

import sys
from multiprocessing import Process


class FileObj:
    def __init__(self, name, size) -> None:
        self.name = name
        self.size = size
        

def divide_content(file: str, n_of_processes: int, word: str, mode: str):
    p_list = []
   
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        n_of_lines = len(lines)
        division = n_of_lines // n_of_processes
        rest = n_of_lines % n_of_processes

        lines_per_process = [0 for i in range(n_of_processes)]
       
        pos = 0
        for i in range(0, n_of_lines-rest, division):
            lines_per_process[pos] += division
            if rest > 0:
                lines_per_process[pos] += 1
                rest -= 1
               
            pos += 1
            if pos == n_of_processes:
                pos = 0
              
        for i in range(n_of_processes):
            a = 0 if i == 0 else lines_per_process[i-1]
            b = lines_per_process[0] if i == 0 else lines_per_process[i-1]+lines_per_process[i]
            lines_args = lines[a:b]
            p = Process(target=find_word_in_text, args=(word,
                                                        lines_args,
                                                        mode))
            p_list.append(p)
            p.start()
       
    for p in p_list:
        p.join()
                     
   
def assign_files_to_processes(files: list, n_of_processes: int, word: str, mode: str):
    def sum_files_sizes(files_list: list):
        '''
        sums the sizes of the files in a group. if list is empty, returns 0
        '''
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
    
        file_group_list = [[] for i in range(n_of_processes)] # [[], [], []]
        print(file_group_list)
        
        for file_obj in file_obj_list: 
            lowest_index = 0
            lowest_sum = sum_files_sizes(file_group_list[0])
            
            for i, file_group in enumerate(file_group_list):
                if sum_files_sizes(file_group) < lowest_sum:
                    lowest_sum = sum_files_sizes(file_group)
                    lowest_index = i
            
            file_group_list[lowest_index].append(file_obj)
            
        files_sub_list = [[f.name for f in file_group] for file_group in file_group_list]
        
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
    # print(files)
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
