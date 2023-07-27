from termcolor import colored

def run(input_dir, output_dir):
    while True:
        print(colored(f'''
        Current Input Directory: {input_dir}
        Current Output Directory: {output_dir}
     ┌──────────────────────────────────────────────────────────────────────────────┐
     |                        AUTOCAPTION PLUS (PREVIEW)                            |
     |------------------------------------------------------------------------------|
     |                                                                              |
     |              Settings                                                        | 
     |                                                                              |
     |          1 - Minimum length (15)                                             |
     |          2 - Maximum length (48)                                             |
     |          3 - Save caption as filename (OFF)                                  |
     |          4 - Save caption to metadata (ON)                                   |  
     |          5 - Save caption to new .txt file (ON)                              |
     |          6 - Append existing caption (OFF)                                   |
     |          7 - New line before [1] after [2] or none [3] (OFF)                 |                    
     |          8 - Preserve Originals (Save to Output Folder) (OFF)                |        
     |          9 - Recursive (Off)                                                 |  
     |                                                                              |
     └──────────────────────────────────────────────────────────────────────────────┘
     |      I - Set Input     O - Set Output     R - Run     X - Exit to Menu       |
     └──────────────────────────────────────────────────────────────────────────────┘
                          
        MODULE IS UNDER CONSTRUCTION 
        
        ''', 'yellow', 'on_blue'))

        choice = input("Please enter X to return to the main menu: ").upper()
        if choice == 'X':
            break
