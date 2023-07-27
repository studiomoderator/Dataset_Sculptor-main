import os
from termcolor import colored
from PIL import Image
import glob
import shutil

class ReduceImage:

    def __init__(self):
        self.input_dir = ""
        self.output_dir = ""
        self.max_image_length = 2048
        self.preserve_originals = False
        self.recursive = False

    def set_input_dir(self, input_dir):
        if os.path.isdir(input_dir):
            self.input_dir = input_dir
        else:
            print("Not valid, no changes made")

    def set_output_dir(self, output_dir):
        if os.path.isdir(output_dir):
            self.output_dir = output_dir
        else:
            print("Not valid, no changes made")

    def display_menu(self):
        print(colored(f'''
    Current Input Directory: {self.input_dir}
    Current Output Directory: {self.output_dir}
    ┌──────────────────────────────────────────────────────────────────────────────┐
    |                             REDUCE IMAGE MODULE                              |
    |------------------------------------------------------------------------------|
    |                                                                              |
    |              Settings                                                        | 
    |                                                                              |
    |          1 - Maximum Image Length ({self.max_image_length})                                   
    |          2 - Preserve Originals (Save to Output Folder) ({'On' if self.preserve_originals else 'Off'})                                          
    |          3 - Recursive ({'On' if self.recursive else 'Off'})                                          
    |                                                                              |
    └──────────────────────────────────────────────────────────────────────────────┘
    |      I - Set Input     O - Set Output     R - Run     X - Exit to Menu       |
    └──────────────────────────────────────────────────────────────────────────────┘
    ''', 'cyan'))

        print("Module resizes images larger than Maximum Image Length to that length")
        print("Preserve Originals will save resized out to a new folder in Output (Be aware this will split up your dataset)")
        print("Recursive ON processes subfolders of the input directory\n")

    def resize_images(self):
        resized_images = 0
        total_files = 0

        path_pattern = self.input_dir.rstrip('/') + ('/**/*.*' if self.recursive else '/*.*')
        for filename in glob.iglob(path_pattern, recursive=self.recursive):
            total_files += 1
            file_ext = filename.rsplit('.', 1)[-1].lower()
            if file_ext in ('png', 'jpg', 'jpeg', 'bmp', 'tif', 'tiff'):
                with Image.open(filename) as img:
                    width, height = img.size
                    if max(width, height) > self.max_image_length:
                        print(f"Rescaling: {filename}")
                        # maintain aspect ratio
                        aspect_ratio = width / height
                        if width > height:
                            new_width = self.max_image_length
                            new_height = int(new_width / aspect_ratio)
                        else:
                            new_height = self.max_image_length
                            new_width = int(new_height * aspect_ratio)

                        img = img.resize((new_width, new_height), Image.LANCZOS)
                        if self.preserve_originals:
                            relative_dir = os.path.dirname(os.path.relpath(filename, self.input_dir))
                            save_dir = os.path.join(self.output_dir.rstrip('/') + "/DS_Reduced", relative_dir)
                            os.makedirs(save_dir, exist_ok=True)
                            img.save(os.path.join(save_dir, os.path.basename(filename)))

                            # copy matching .txt file if it exists
                            txt_file = os.path.splitext(filename)[0] + '.txt'
                            if os.path.isfile(txt_file):
                                shutil.copy(txt_file, save_dir)
                        else:
                            img.save(filename)
                        resized_images += 1

        print(f'Total images processed: {total_files}')
        print(f'Total images resized: {resized_images}')

    def run(self):
        while True:
            self.display_menu()
            choice = input("Enter your selection: ")

            if choice == '1':
                self.max_image_length = int(input("Enter Maximum Image Length in Pixels (Images will be scaled down to this length on longer side): "))
            elif choice == '2':
                user_input = input("Save resized images to Output Directory? (Y/N)").lower()
                self.preserve_originals = user_input in ['y', 'yes']
            elif choice == '3':
                user_input = input("Process folders recursively? (Y/N)").lower()
                self.recursive = user_input in ['y', 'yes']
            elif choice.lower() == 'i':
                new_input_dir = input("Change Input Directory: ")
                self.set_input_dir(new_input_dir)
            elif choice.lower() == 'o':
                new_output_dir = input("Change Output Directory: ")
                self.set_output_dir(new_output_dir)
            elif choice.lower() == 'r':
                confirm = input("WARNING: Module will downscale all larger images to the specified size\nDataset Cleaner is experimental and only intended for backed up datasets\nUse only on backed up datasets and at your own risk\nRun the module? (Y/N) ")
                if confirm.lower() in ['y', 'yes']:
                    self.resize_images()
            elif choice.lower() == 'x':
                break
            else:
                print("Invalid choice. Please choose a valid option or press 'x' to exit.")

