import os
from termcolor import colored
from PIL import Image
import glob
import shutil

SUPPORTED_FILETYPES = ['bmp', 'dib', 'eps', 'gif', 'icns', 'ico', 'im', 'jpeg', 'msp', 'pcx', 'png', 'ppm', 'sgi', 'spider', 'tiff', 'webp', 'xbm', 'jpg', 'tif', 
                       'BMP', 'DIB', 'EPS', 'GIF', 'ICNS', 'ICO', 'IM', 'JPEG', 'MSP', 'PCX', 'PNG', 'PPM', 'SGI', 'SPIDER', 'TIFF', 'WEBP', 'XBM', 'JPG', 'TIF']

class ImageConverter:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.target_filetype = ".png"
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
    |                            IMAGE CONVERTER MODULE                            |
    |------------------------------------------------------------------------------|
    |                                                                              |
    |              Settings                                                        | 
    |                                                                              |
    |          1 - Convert to filetype ({self.target_filetype})                                   
    |          2 - Preserve Originals (Save new to Output Folder) ({'On' if self.preserve_originals else 'Off'})                                          
    |          3 - Recursive ({'On' if self.recursive else 'Off'})                                          
    |                                                                              |
    └──────────────────────────────────────────────────────────────────────────────┘
    |      I - Set Input     O - Set Output     R - Run     X - Exit to Menu       |
    └──────────────────────────────────────────────────────────────────────────────┘
    ''', 'yellow'))

        print("Module will convert non-target_filetype images to target_filetype and delete originals")
        print(f"supported filetypes: bmp dib eps gif icns ico im jpeg jpg msp pcx png ppm sgi spider tif tiff webp xbm")
        print("Preserve Originals ON will save converted images to a folder DS_Converted in Output")
        print("Recursive ON processes subfolders of the input directory\n")

    def convert_images(self):
        converted_images = 0
        print(f"Input directory: {self.input_dir}")  # print input directory
        print(f"Recursive flag: {self.recursive}")   # print recursive flag status

        glob_pattern = '/**/*.*' if self.recursive else '/*.*'
        for filename in glob.iglob(self.input_dir.rstrip('/') + glob_pattern, recursive=self.recursive):
            if filename.lower().split('.')[-1] in SUPPORTED_FILETYPES:
                print(f"Checking file: {filename}")  # print each file being checked
                # Skip converting if file is already in target format
                if filename.lower().split('.')[-1] == self.target_filetype[1:]:
                    print(f"File {filename} already in target format, skipping.")
                    continue
                with Image.open(filename) as img:
                    new_filename = '.'.join(filename.split('.')[:-1]) + self.target_filetype
                    if self.preserve_originals:
                        rel_path = os.path.relpath(filename, self.input_dir)  # Get relative path
                        save_dir = os.path.join(self.output_dir, "DS_Converted", os.path.dirname(rel_path))
                        os.makedirs(save_dir, exist_ok=True)
                        img.save(os.path.join(save_dir, os.path.basename(new_filename)))
                        # Check for the existence of a caption file and copy it if found
                        caption_file = filename.rsplit('.', 1)[0] + '.txt'
                        if os.path.isfile(caption_file):
                            shutil.copy(caption_file, save_dir)
                    else:
                        img.save(new_filename)
                        # If not preserving originals, delete original file after successful conversion
                        os.remove(filename)
                        print(f"Original file {filename} deleted.")
                    converted_images += 1

        print(f'Total images converted: {converted_images}')

        print(f'Total images converted: {converted_images}')

    def run(self):
        while True:
            self.display_menu()
            choice = input("Enter your selection: ")

            if choice == '1':
                target_filetype = '.' + input("Enter target filetype (without dot): ").lower()
                if target_filetype[1:] in SUPPORTED_FILETYPES:
                    self.target_filetype = target_filetype
                else:
                    print(f"Not a valid filetype. No changes made. Supported filetypes are {', '.join(SUPPORTED_FILETYPES)}")
            elif choice == '2':
                user_input = input("Save converted images to Output Directory? (Y/N)").lower()
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
                confirm = input("WARNING: Module will convert all images to the specified format and delete originals\nDataset Sculptor is experimental and only intended for backed up datasets\nUse only on backed up datasets and at your own risk\nRun the module? (Y/N) ")
                if confirm.lower() in ['y', 'yes']:
                    self.convert_images()
            elif choice.lower() == 'x':
                break
            else:
                print("Invalid choice. Please choose a valid option or press 'x' to exit.")
