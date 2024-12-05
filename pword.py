### Grupo: SO-TI-04
# Aluno 1: Libero Suprani (fc62220)
# Aluno 2: Ravi Mughal (fc62504)
# Aluno 3: Ricardo Avelãs (fc62257)

# ex: ./pword -m c -p 1 -w exemplo ficheiro1.txt

import sys, signal, os, re
from multiprocessing import Process, Value, Array, Queue, Lock, Semaphore

mutex = Lock()
shared_counter = None
shared_found = Queue()
my_index = -1
process_list = []
is_terminated = Value("i", 0)
is_plummer_needed = False
unclog = []

class FileObj:
    '''
    Representation of a file.
    '''
    def __init__(self, name, size) -> None:
        self.name = name
        self.size = size
        

def divide_content(filename: str, n_of_processes: int, word: str, mode: str):
    '''
    Divides the content of a given file between n-processes.
    
    Requires: 
    - filename, word, mode str
    - n_of_processes int
    
    Ensures:
    - Creation and start of n-processes, where each process deals with a part of the content of the file.
    '''
    
    global shared_counter
    global my_index
    global process_list
    global is_plummer_needed
    global unclog
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            n_of_lines = len(lines)
            
            if n_of_lines == 0:
                find_word_in_text(word, "", mode)
                return
            
            division = n_of_lines // n_of_processes
            rest = n_of_lines % n_of_processes

            lines_per_process = [0 for i in range(n_of_processes)]
        
            # this cicle assigns the amount of lines each process is gonna receive,
            # incrementing to each position of the array the result of division 
            # (and +1 while there is rest available)
            pos = 0
            for i in range(0, n_of_lines-rest, division):
                lines_per_process[pos] += division
                if rest > 0:    
                    lines_per_process[pos] += 1
                    rest -= 1
                
                pos += 1
                if pos == n_of_processes:
                    pos = 0
                
            # passes the exact lines each process is gonna handle, based in lines_per_process
            start_pos = 0
            finish_pos = 0
            for i in range(n_of_processes):
                finish_pos = start_pos + lines_per_process[i]
                lines_args = lines[start_pos:finish_pos]
                
                text_block = ""
                for line in lines_args:
                    text_block += line
                
                p = Process(target=find_word_in_block, args=(word, text_block, mode))
                process_list.append(p)
                
                p.start()
                start_pos = finish_pos
                
            for p in process_list:
                print(is_plummer_needed)
                if is_plummer_needed:
                    unclog.append(call_plummer()) if mode == "i" else unclog.extend(call_plummer())
                    print(len(unclog))
                p.join()
                         
    except FileNotFoundError:
        print(f"Erro! Ficheiro '{filename}' não encontrado.")    
   
                     
def assign_files_to_processes(files: list, n_of_processes: int, word: str, mode: str):
    '''
    Divides the files among n-processes.
    
    Requires:
    - files list
    - n_of_processes int
    - word, mode str
    
    Ensures:
    - Creation and start of n-processes, where each process deals with 1 or more files.
    '''
    
    def sum_files_sizes(files_list: list):
        '''
        Sums the sizes of the files in a group. 
        
        Requires:
        - files_list list
        
        Returns: 
        Total amount of lines in list of files. If files_list is empty, returns 0. 
        '''
        res = 0
        if len(files_list) == 0:
            return 0
        for f in files_list:
            res += f.size
        return res
    
    global shared_counter
    global my_index
    global process_list
    global is_plummer_needed
    global unclog
    
    # creates and runs each process passing exactly 1 file to it
    if n_of_processes == len(files):
        for i in range(n_of_processes):
            p = Process(target=find_word_in_files, args=(word, [files[i]], mode))
            process_list.append(p)
            p.start()
            
        for p in process_list:
            print(is_plummer_needed)
            if is_plummer_needed:
                unclog.append(call_plummer()) if mode == "i" else unclog.extend(call_plummer())
                print(len(unclog))
            p.join()
    else:
        # converts each file to a FileObj
        file_obj_list = []  
        for i, filename in enumerate(files):
            try:
                with open(filename, 'r', encoding="utf-8") as f:               
                    lines = f.readlines()
                    file_obj_list.append(FileObj(name=filename, size=len(lines)))
            except FileNotFoundError:
                print(f"Erro! Ficheiro '{filename}' não encontrado.")
        file_group_list = [[] for i in range(n_of_processes)] # [[], []]
        
        # this loop will find the group of files that has the least amount of total lines at the moment
        # and will assign a file to this group
        for file_obj in file_obj_list: 
            lowest_index = 0
            lowest_sum = sum_files_sizes(file_group_list[0])
            
            # finds the group of files that has the least amount of lines combined 
            for i, file_group in enumerate(file_group_list):
                if sum_files_sizes(file_group) < lowest_sum:
                    lowest_sum = sum_files_sizes(file_group)
                    lowest_index = i
            
            # appends the current file to the group with the lowest amount of lines combined
            file_group_list[lowest_index].append(file_obj)
            
        # converts the file_objects in the groups to their respective names
        files_sub_list = [[f.name for f in file_group] for file_group in file_group_list]
        
        for sub_list in files_sub_list:
            p = Process(target=find_word_in_files, args=(word, sub_list, mode))
            process_list.append(p)
            p.start()
            
        for p in process_list:
            print(is_plummer_needed)
            if is_plummer_needed:
                unclog.append(call_plummer()) if mode == "i" else unclog.extend(call_plummer())
                print(len(unclog))
            p.join()


def find_my_index():
    """
    Finds the index of shared_found Array that this current Process must use (which is the first with the value -1), changing the value
    of global variable my_index to this index
    """
    global my_index
    
    found_my_index = False
    my_index = 0
    my_index_iterator = 0
    while not found_my_index:
        found_my_index = True if shared_counter[my_index_iterator] == -1 else False
        my_index = my_index_iterator 
        my_index_iterator += 1
       
            
def find_word_in_text(word: str, text: str, mode): 
    '''
    Finds a given word in a given text.
    
    Requires:
    - word, text, mode str
    
    Ensures:
    - Print of the amount of occurrences of the word in the text, depending of the mode chosen. 
    '''
    global shared_counter
    global shared_found
    global my_index
    counter = 0
    
    if mode == 'c':
        # mutex start
        mutex.acquire()
        shared_counter.value += text.count(word)
        mutex.release()
        # mutex end
        return None
    
    elif mode == 'l':
        # mutex start
        mutex.acquire()    
        split_text = text.strip().split("\n")
        lines_containing_word = [i for i in split_text if re.search(rf"{word}", i)]
        
        # increments the shared array in my_index position with the amount of lines found so far
        shared_counter[my_index] += len(lines_containing_word)       
        mutex.release()
        # mutex end
        
        # return set(lines_found) //TODO tem que ver com a prof se precisa ser set ou não
        return lines_containing_word
    
    elif mode == "i":
        mutex.acquire()

        counter = len(re.findall(rf"\b{word}\b", text))
        
        # puts the counter in the queue after each file/block was analyzed    
        # shared_found.put(counter)
        shared_counter[my_index] += counter
                
        mutex.release()
        return counter


def find_word_in_block(word: str, block: str, mode):
    
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    global my_index
    global shared_counter
    global is_terminated
    
    if mode != "c":
        find_my_index()
        shared_counter[my_index] = 0
       
    if is_terminated.value == 0:
        list_of_results = []
        
        result = find_word_in_text(word, block, mode)

        if mode == "l":
            list_of_results.extend(result)
        if mode == "i":
            list_of_results.append(result)
        
        shared_found.put(list_of_results)
        
    
    
def find_word_in_files(word: str, files: list, mode):
    '''
    Calls find_word_in_text for every file in files.
    '''
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    
    global my_index
    global shared_counter
    global is_terminated
    
    if mode != "c":
        find_my_index()
        shared_counter[my_index] = 0
    
    # list_of_results = set() if mode == "l" else []
    list_of_results = []
    
    if is_terminated.value == 0:
        for filename in files:
            if is_terminated.value == 1:
                break
            try:
                with open(filename, 'r', encoding="utf-8") as f:
                    text = f.read()
                    result = find_word_in_text(word, text, mode)
                    if mode == "l":
                        list_of_results.extend(result)

                    if mode == "i":
                        list_of_results.append(result)
            except FileNotFoundError:
                print(f"Erro! Ficheiro '{filename}' não encontrado.")
    
        # if mode is "l", put in the queue the list of lines after all the files were analyzed
        # if mode == "l":
        shared_found.put(list_of_results)
            
    
# --------------------------------------------------  

def terminate_early():
    '''
    '''
    global mode
    global shared_found
    global is_terminated
        
    is_terminated.value = 1
        
    # if mode == "l":
        #TODO do something
        # print(f"Linhas encontradas: {shared_found}")
        
    # os.kill()
    pass
    

def call_plummer():
    unclogged = None
    while unclogged is None:
        if shared_found.qsize() > 0:
            unclogged = shared_found.get()
            print(f"unclogged {unclogged}")
            return unclogged
        

def pword(args: list):
    
    signal.signal(signal.SIGINT, terminate_early)
    
    global shared_found
    global shared_counter
    global n_of_processes
    global is_plummer_needed
    global unclog
    # global mode
    
    mode = args[0]
    n_of_processes = int(args[1])
    interval = int(args[2])               
    partial_results_file = args[3]
    word = args[4]
    files = args[5:]
    
    if len(files) == 1 and n_of_processes > 1: # 1 file and multiple processes
        with open(files[0], "r") as f:
            lines = f.readlines()
            n_of_lines = len(lines)
            
            if n_of_processes > n_of_lines:
                n_of_processes = n_of_lines
                
        mutex.acquire()
        if mode == "c":
            if shared_counter == None:
                shared_counter = Value("i", 0)
        else:
            if shared_counter == None:
                is_plummer_needed = True
                shared_counter = Array("i", [-1 for i in range(n_of_processes)])
        mutex.release()

        divide_content(files[0], n_of_processes, word, mode)
        # TODO do something else
        
    else:
        if n_of_processes > len(files):
            n_of_processes = len(files)
            
        mutex.acquire()
        if mode == "c":
            if shared_counter == None:
                shared_counter = Value("i", 0)
        else:
            if shared_counter == None:
                is_plummer_needed = True
                shared_counter = Array("i", [-1 for i in range(n_of_processes)])
        mutex.release()
        
        assign_files_to_processes(files, n_of_processes, word, mode)    


    if mode == "c":
        print(f"(PAI) Ocorrências: {shared_counter.value}")
    
    if mode == "l":
        all_lines_set = []
        print(f"eu sou o unclog: {unclog}")
        for line_set in unclog:
            all_lines_set.append(line_set)
            
        print(f"(PAI) Linhas encontradas: {len(all_lines_set)}")
        
    elif mode == "i":
        all_occurrences = []
        
        for occurrences in unclog:
        # ele recebe o unclog como, por exemplo [[1, 2020]], por causa do append la em cima
            all_occurrences.extend(occurrences)
        
        print(f"(PAI) Todas as ocorrências: {sum(all_occurrences)}")
                
                
# --------------------------------------------------   

def main(args):
    pword(args)

if __name__ == "__main__":
    main(sys.argv[1:])
