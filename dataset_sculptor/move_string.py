import os
import glob
import shutil
from termcolor import colored

class MoveString:
    """A class to move or copy files based on a filename string."""
    
    def __init__(self):
        self.input_dir = ""
        self.output_dir = ""
        self.search_string = ""
        self.copy_or_move = "MOVE"
        self.recursive = False

    def set_input_dir(self, input_dir):
        """Set the input directory and output directory based on it."""
        if os.path.isdir(input_dir):
            self.input_dir = input_dir
            self.output_dir = os.path.join(input_dir, "Output")
        else:
            print("Not valid, no changes made")

    def set_output_dir(self, output_dir):
        """Set the output directory."""
        if os.path.isdir(output_dir):
            self.output_dir = output_dir
        else:
            print("Not valid, no changes made for output directory")

    def display_menu(self):
        """Display the settings menu for the user."""
        print(colored(f'''
    Current Input Directory: {self.input_dir}
    Current Output Directory: {self.output_dir}
    ┌──────────────────────────────────────────────────────────────────────────────┐
    |                     MOVE BASED ON FILENAME STRING MODULE                     |
    |------------------------------------------------------------------------------|
    |                                                                              |
    |              Settings                                                        | 
    |                                                                              |
    |          1 - Move String ({self.search_string or "NONE"})
    |          2 - Copy or Move ({self.copy_or_move})                                             
    |          3 - Recursive ({'ON' if self.recursive else 'OFF'})                                                 
    |                                                                              |
    └──────────────────────────────────────────────────────────────────────────────┘
    |          I - Set Input         R - Run         X - Exit to Menu              |
    └──────────────────────────────────────────────────────────────────────────────┘
    ''', 'light_cyan'))

        print("Module allows user to copy or move a file based on a string in the filename to a DS_String folder in the Output Folder")
        print("Minimum is 3 characters to avoid false positives")
        print("Move will relocate originals, Copy will leave originals in place and make a new copy in DS_String")
        print("Recursive ON processes subfolders of the input directory\n")

    def move_or_copy_files(self):
        """Move or copy files based on the given settings."""
        moved_or_copied_files = 0
        path_pattern = self.input_dir.rstrip('/') + ('/**/*.*' if self.recursive else '/*.*')

        for filename in glob.iglob(path_pattern, recursive=self.recursive):
            if self.search_string in filename:
                print(f"{'Moving' if self.copy_or_move == 'MOVE' else 'Copying'}: {filename}")
                destination_dir = os.path.join(self.output_dir.rstrip('/'), "DS_String")
                os.makedirs(destination_dir, exist_ok=True)
                shutil.move(filename, destination_dir) if self.copy_or_move == "MOVE" else shutil.copy(filename, destination_dir)
                moved_or_copied_files += 1

        print(f'Total files {self.copy_or_move.lower()}d: {moved_or_copied_files}')

    def handle_menu_choice(self, choice):
        """Handle user choice from the menu."""
        if choice == '1':
            self.set_search_string()
        elif choice == '2':
            self.set_copy_or_move()
        elif choice == '3':
            self.set_recursive()
        elif choice.lower() == 'i':
            self.change_input_dir()
        elif choice.lower() == 'r':
            self.confirm_and_run()
        elif choice.lower() == 'x':
            return False
        else:
            print("Invalid choice. Please choose a valid option or press 'x' to exit.")
        return True

    def set_search_string(self):
        """Prompt user for search string and validate it."""
        self.search_string = input("Enter Filename String to Search: ")
        if len(self.search_string) < 3:
            print("String too short. Please provide a string of at least 3 characters.")
            self.search_string = ""

    def set_copy_or_move(self):
        """Prompt user for copying or moving choice."""
        user_input = input("Would you like to Copy [1] or Move [2] the images?: ")
        self.copy_or_move = "COPY" if user_input in ['1', 'copy'] else "MOVE"

    def set_recursive(self):
        """Prompt user for recursive choice."""
        user_input = input("Process folders recursively? (Y/N): ").lower()
        self.recursive = user_input in ['y', 'yes']

    def change_input_dir(self):
        """Prompt user to change input directory."""
        new_input_dir = input("Change Input Directory: ")
        self.set_input_dir(new_input_dir)

    def confirm_and_run(self):
        """Confirm with the user and run the move/copy operation."""
        confirm = input("WARNING: Module will move or copy files with supplied string\nDataset Cleaner is experimental and only intended for backed up datasets\nUse only on backed up datasets and use at your own risk\nRun the module? (Y/N) ")
        if confirm.lower() in ['y', 'yes']:
            self.move_or_copy_files()

    def run(self):
        """Main loop to run the module."""
        while True:
            self.display_menu()
            choice = input("Enter your selection: ")
            if not self.handle_menu_choice(choice):
                break

# To run the MoveString module
# if __name__ == '__main__':
#     mover = MoveString()
#     mover.run()
