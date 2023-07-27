import os
import shutil
from PIL import Image, ImageStat
from termcolor import colored

append_option_map = {'1': 'Monochrome', '2': 'Black and White', '3': 'Greyscale', '4': 'All'}
move_or_copy_map = {'1': 1, '2': 2, '3': None}
VALID_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".tif", ".JPG", ".JPEG", ".PNG", ".BMP", ".GIF", ".TIFF", ".TIF"]

def is_valid_path(path):
    return os.path.exists(path)


class BWImageMenu:

    def __init__(self, settings):
        self.input_dir = settings["INPUT_DIR"]
        self.output_dir = settings["OUTPUT_DIR"]
        self.mse_cutoff = settings["MSE_CUTOFF"]
        self.should_label_filename = settings["LABEL_FILENAME"]
        self.append_caption = settings["APPEND_CAPTION"]
        self.copy_or_move = settings["MOVE_OR_COPY"]
        self.recursive = settings["RECURSIVE"]

    def display_menu(self):
        # you can include the interactive part of your menu here, get user input, etc
        # for now, it only displays the menu

        caption_map = {1: "Monochrome", 2: "Black and White", 3: "Greyscale", 4: "All", None: "NONE"}  # Include None for the default case
        print(colored(f'''
        
        Current Input Directory: {self.input_dir}
        Current Output Directory: {self.output_dir}
    ┌──────────────────────────────────────────────────────────────────────────────┐
    |                        BLACK AND WHITE IMAGE MODULE                          |
    |------------------------------------------------------------------------------|
    |                                                                              |
    |              Settings                                                        | 
    |                                                                              |
    |          1 - Mean Squared Error Cutoff ({self.mse_cutoff})                                   
    |          2 - Rename image with a _BW label ({'YES' if self.should_label_filename else 'NO'})                                       
    |          3 - Append caption with a label ({caption_map[self.append_caption]})                                          
    |          4 - Copy [1], move[2] or leave file in place[3]: ({self.copy_or_move or 'NONE'})       
    |          5 - Recursive? ({'YES' if self.recursive else 'NO'})                                         
    |                                                                              |
    └──────────────────────────────────────────────────────────────────────────────┘
    |      I - Set Input     O - Set Output     R - Run     X - Exit to Menu       |
    └──────────────────────────────────────────────────────────────────────────────┘
    ▓▓▓▓▓▓▓▓▓▓██████████▓▓▓▓▓▓▓▓▓▓██████████▓▓▓▓▓▓▓▓▓▓██████████▓▓▓▓▓▓▓▓▓▓██████████
        ''', 'grey', 'on_light_grey'))

        print("Module identifies black and white images")
        print("Tweak Mean Squared Error Cuttoff to find the threshold for your images")
        print("Higher cutoff means more images identified as greyscale, with more false positive potential")
        print("Labeling adds a _BW label to the end of the filename")
        print("Append Caption saves the terms 'Monochrome, Black and White Image' to the end of the paired caption")
        print("Copy or move to the Output subfolder DS_Monochrome")
        print("Recursive ON processes subfolders of the input directory\n")

    def run(self):
        total_images_affected = 0
        total_captions_affected = 0
        print(f"Input directory: {self.input_dir}")  # print input directory
        print(f"Recursive flag: {self.recursive}")   # print recursive flag status

        for root, dirs, files in os.walk(self.input_dir):
            for filename in files:
                print(f"Checking file: {filename}")  # print each file being checked
                if self.detect_bw_image(os.path.join(root, filename), MSE_cutoff=self.mse_cutoff):
                    image_affected = False  # Set a flag to check if this image was affected
                    if self.should_label_filename:
                        self.label_filename(root, filename)
                        image_affected = True
                    if self.append_caption:
                        if self.apply_append_caption(root, os.path.join(self.output_dir, 'DS_Monochrome'), filename, self.copy_or_move, self.append_caption):
                            total_captions_affected += 1
                            image_affected = True
                    if self.copy_or_move != 3:
                        print(f"copy_or_move: {self.copy_or_move}")  # print copy_or_move flag
                        self.copy_or_move_file(root, self.output_dir, filename, self.copy_or_move)
                        image_affected = True

                    if image_affected:  # Only increment if the image was truly affected
                        total_images_affected += 1

        print(f"Total images affected: {total_images_affected}")
        print(f"Total captions affected: {total_captions_affected}")


    def detect_bw_image(self, image_path, thumb_size=40, MSE_cutoff=22, adjust_color_bias=True):
        if os.path.splitext(image_path)[1].lower() not in VALID_IMAGE_EXTENSIONS:
            return False
        try:
            pil_img = Image.open(image_path)
        except IOError:
            print(f"Unable to open image: {image_path}")
            return False
        bands = pil_img.getbands()
        if bands == ('R','G','B') or bands== ('R','G','B','A'):
            thumb = pil_img.resize((thumb_size,thumb_size))
            SSE, bias = 0, [0,0,0]
            if adjust_color_bias:
                bias = ImageStat.Stat(thumb).mean[:3]
                bias = [b - sum(bias)/3 for b in bias ]
            for pixel in thumb.getdata():
                pixel = [x / 255.0 for x in pixel]  # normalize pixel values
                mu = sum(pixel)/3
                SSE += sum((pixel[i] - mu - bias[i])*(pixel[i] - mu - bias[i]) for i in [0,1,2])
            MSE = float(SSE)/(thumb_size*thumb_size)
            if MSE <= MSE_cutoff:
                return True  # grayscale
            else:
                return False  # color
        elif len(bands)==1:
            return True  # black and white
        else:
            return False  # unknown
    
    def apply_append_caption(self, input_path, output_path, filename, action_choice, caption_choice):
        caption_map = {1: "Monochrome", 2: "Black and White", 3: "Greyscale", 4: "Monochrome, Black and White, Greyscale"}
        base, extension = os.path.splitext(filename)
        caption_file_input = os.path.join(input_path, base + ".txt")

        if os.path.exists(caption_file_input):
            if action_choice == 1:  # If copying, modify caption in the output directory
                caption_file_output = os.path.join(output_path, base + ".txt")
                shutil.copy(caption_file_input, caption_file_output)
                caption_file_to_modify = caption_file_output
            else:  # If moving, modify caption in the input directory
                caption_file_to_modify = caption_file_input

            with open(caption_file_to_modify, "a") as file:
                file.write(f", {caption_map[caption_choice]}")
            print(f"Adjusted caption file: {caption_file_to_modify}")  # print the name of the caption file being adjusted
            return True  # return True if a caption file was modified
        return False  # return False if no caption file was found
    
    def copy_or_move_file(self, input_path, output_path, filename, action_choice):
        base, extension = os.path.splitext(filename)
        new_filename = filename
        if self.should_label_filename:
            new_filename = f"{base}_BW{extension}"
        new_output_path = os.path.join(output_path, 'DS_Monochrome')
        if not os.path.exists(new_output_path):
            os.makedirs(new_output_path)
        try:
            old_filepath = os.path.join(input_path, filename)
            new_filepath = os.path.join(new_output_path, new_filename)
            if action_choice == 1:  # Copy
                shutil.copy(old_filepath, new_filepath)
                if self.append_caption:
                    self.apply_append_caption(new_output_path, new_output_path, new_filename, action_choice, self.append_caption)
            elif action_choice == 2:  # Move
                shutil.move(old_filepath, new_filepath)
                print(f"File moved to: {new_filepath}")  # print the directory where the file is being moved
                if os.path.exists(new_filepath) and not os.path.exists(old_filepath):
                    print(f"Move successful for file: {filename}")
                else:
                    print(f"Move unsuccessful for file: {filename}")
                if self.append_caption:
                    self.apply_append_caption(new_output_path, new_output_path, new_filename, action_choice, self.append_caption)
            else:
                print(f"Invalid action choice for file: {filename}")
        except IOError:
            print(f"Unable to perform the operation on file: {filename}")

        # Move/Copy the caption file if it exists
        base, extension = os.path.splitext(filename)
        caption_filename = f"{base}.txt"
        caption_input_path = os.path.join(input_path, caption_filename)
        caption_output_path = os.path.join(new_output_path, caption_filename)

        if os.path.exists(caption_input_path):
            try:
                if action_choice == 1:  # Copy
                    shutil.copy(caption_input_path, caption_output_path)
                elif action_choice == 2:  # Move
                    shutil.move(caption_input_path, caption_output_path)
            except IOError:
                print(f"Unable to perform the operation on caption file: {caption_filename}")

    def label_filename(self, path, filename):
        base, extension = os.path.splitext(filename)
        new_filename = f"{base}_BW{extension}"
        os.rename(os.path.join(path, filename), os.path.join(path, new_filename))
        
        # rename the matching caption file if it exists
        caption_file = os.path.join(path, base + ".txt")
        if os.path.exists(caption_file):
            new_caption_file = f"{base}_BW.txt"
            os.rename(caption_file, os.path.join(path, new_caption_file))

        
def main_execution_loop(input_dir, output_dir):
    settings = {
        "INPUT_DIR": input_dir,
        "OUTPUT_DIR": output_dir,
        "MSE_CUTOFF": 22,
        "LABEL_FILENAME": False,
        "APPEND_CAPTION": None,
        "MOVE_OR_COPY": None,
        "RECURSIVE": False,
    }
    
    bw_menu = BWImageMenu(settings)
    while True:
        bw_menu.display_menu()
        option = input("Enter your selection: ").strip().lower()

        if option == '1':
            MSE_cutoff = input("Enter Threshold (Mean Squared Error Cutoff value): ")
            if MSE_cutoff.isdigit():
                bw_menu.mse_cutoff = int(MSE_cutoff)
            else:
                print("Invalid input. Please enter a number.")
        elif option == '2':
            should_label_filename = input("Rename image with a _BW label? (Y/N): ").strip().lower()
            bw_menu.should_label_filename = True if should_label_filename == 'y' else False
        elif option == '3':
            append_caption = input("Append caption with a label? (Y/N): ").strip().lower()
            if append_caption == 'y':
                append_option = input("Choose the label Monochrome [1], Black and White [2], or Greyscale [3] or *All* [4]: ").strip()
                if append_option.isdigit() and 1 <= int(append_option) <= 4:
                    bw_menu.append_caption = int(append_option)
                else:
                    print("Invalid option, no changes made.")
            else:
                bw_menu.append_caption = None
        elif option == '4':
            move_or_copy = input("Copy [1], move[2] or leave file in place[3]: (1/2/3) ").strip()
            bw_menu.copy_or_move = move_or_copy_map.get(move_or_copy)  # No need for the default value, get will return None if the key isn't found
        elif option == '5':
            recursive = input("Process folders recursively? (Y/N): ").strip().lower()
            bw_menu.recursive = True if recursive == 'y' else False
        elif option == 'i':
            input_dir = input("Change Input Directory: ").strip()
            if os.path.isdir(input_dir):
                bw_menu.input_dir = input_dir
            else:
                print("Not valid, no changes made")
        elif option == 'o':
            output_dir = input("Change Output Directory: ").strip()
            if os.path.isdir(output_dir):
                bw_menu.output_dir = output_dir
            else:
                print("Not valid, no changes made")
        elif option == 'r':
            print("WARNING: Dataset Cleaner is experimental and only intended for backed up datasets")
            print("Use only on backed up datasets and at your own risk")
            confirmation = input("Run the module? (Y/N): ").strip().lower()
            if confirmation == 'y':
                bw_menu.run()
        elif option == 'x':
            break
        else:
            print("Invalid option, please try again.")
