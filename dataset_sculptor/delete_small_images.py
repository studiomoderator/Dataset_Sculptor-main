import os
from termcolor import colored
from PIL import Image
import glob

SUPPORTED_FORMATS = ['.bmp', '.png', '.jpeg', '.jpg', '.tiff', '.gif', '.ico', '.pcx', '.ppm', '.webp']

class DeleteSmallImages:

    def __init__(self):
        self.input_dir = ""
        self.min_image_length = 512
        self.delete_orphan_captions = True
        self.recursive = False

    def set_input_dir(self, input_dir):
        if os.path.isdir(input_dir):
            self.input_dir = input_dir
        else:
            print("Not valid, no changes made")

    def display_menu(self):
        print(colored(f'''
    Current Input Directory: {self.input_dir}
    ┌──────────────────────────────────────────────────────────────────────────────┐
    |                         DELETE SMALL IMAGES MODULE                           |
    |------------------------------------------------------------------------------|
    |                                                                              |
    |              Settings                                                        | 
    |                                                                              |
    |          1 - Minimum Image Length ({self.min_image_length})                                   
    |          2 - Delete Orphan Captions ({'On' if self.delete_orphan_captions else 'Off'})              
    |          3 - Recursive ({'On' if self.recursive else 'Off'})                                          
    |                                                                              |
    └──────────────────────────────────────────────────────────────────────────────┘
    |          I - Set Input         R - Run         X - Exit to Menu              |
    └──────────────────────────────────────────────────────────────────────────────┘
    ''', 'green'))

        print("Module deletes images smaller than Minimum Image Length on EITHER SIDE")
        print("Delete Orphan Captions set to ON will delete all .txt captions without an image pair")
        print("Recursive ON processes subfolders of the input directory\n")

    def delete_small_images_and_orphans(self):
        # Check if directory is empty
        if not os.listdir(self.input_dir):
            print(f"Directory {self.input_dir} is empty.")
            return

        # Confirm that the correct glob path is being formed
        path_to_scan = self.input_dir.rstrip('/') + ('/**/*.*' if self.recursive else '/*.*')
        print(f"Path to scan: {path_to_scan}")

        deleted_images = 0
        deleted_captions = 0

        for filename in glob.iglob(path_to_scan, recursive=self.recursive):
            print(f"Found file: {filename}")  # Print the file name that glob found
            if filename.lower().endswith(tuple([fmt.lower() for fmt in SUPPORTED_FORMATS] + [fmt.upper() for fmt in SUPPORTED_FORMATS])):
                with Image.open(filename) as img:
                    width, height = img.size
                print(f"File: {filename}, Width: {width}, Height: {height}, Min length: {self.min_image_length}")
                if min(width, height) < self.min_image_length:
                    print(f"Deleting image: {filename}")
                    os.remove(filename)
                    deleted_images += 1
                else:
                    print(f"Not deleting image: {filename}, Width: {width}, Height: {height}")
            elif self.delete_orphan_captions and filename.lower().endswith('.txt'):
                if not (set(glob.glob(filename.rsplit('.', 1)[0] + '.*')) - set(glob.glob(filename))):
                    print(f"Deleting caption: {filename}")
                    os.remove(filename)
                    deleted_captions += 1

        print(f'Total images deleted: {deleted_images}')
        print(f'Total captions deleted: {deleted_captions}')

    def run(self):
        while True:
            self.display_menu()
            choice = input("Enter your selection: ")

            if choice == '1':
                self.min_image_length = int(input("Enter Minimum Image Length in Pixels: "))
            elif choice == '2':
                user_input = input("Delete all .txt Files without a Pair? (Y/N)").lower()
                self.delete_orphan_captions = user_input in ['y', 'yes']
            elif choice == '3':
                user_input = input("Process folders recursively? (Y/N)").lower()
                self.recursive = user_input in ['y', 'yes']
            elif choice.lower() == 'i':
                new_input_dir = input("Change Input Directory: ")
                self.set_input_dir(new_input_dir)
            elif choice.lower() == 'r':
                confirm = input("WARNING: Module will delete all files under specified size\nDataset Cleaner is experimental and only intended for backed up datasets\nUse only on backed up datasets and use at your own risk\nRun the module? (Y/N) ")
                if confirm.lower() in ['y', 'yes']:
                    print(f"Scanning directory: {self.input_dir}")  # Printing the directory being scanned
                    self.delete_small_images_and_orphans()
            elif choice.lower() == 'x':
                break
            else:
                print("Invalid choice. Please choose a valid option or press 'x' to exit.")
