import os
import glob
import exiftool
import json
from termcolor import colored
import time
import shutil

class MetadataCaptionConverter:
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.direction = None  # This will be either 'Caption to Metadata' or 'Metadata to Caption'
        self.save_to_output = False
        self.recursive = False
        self.total_files_processed = 0
        self.failures = 0

    
    def sanitize_string(self, s):
        """
        Replace non-ASCII characters with a placeholder or remove them
        """
        return ''.join([char if ord(char) < 128 else '?' for char in s])
    

    def set_input_dir(self, input_dir):
        # Check if the provided directory is valid
        if not os.path.isdir(input_dir):
            print("Invalid directory. Please provide a valid directory.")
        else:
            self.input_dir = input_dir

    def set_output_dir(self, output_dir):
        # Check if the provided directory is valid
        if not os.path.isdir(output_dir):
            print("Invalid directory. Please provide a valid directory.")
        else:
            self.output_dir = output_dir

    def set_direction(self, direction):
        # Check if the provided direction is valid
        if direction not in ['Caption to Metadata', 'Metadata to Caption']:
            print("Invalid direction. Please choose either 'Caption to Metadata' or 'Metadata to Caption'.")
        else:
            self.direction = direction

    def set_save_to_output(self, save_to_output):
        # Check if the provided value is a boolean
        if not isinstance(save_to_output, bool):
            print("Invalid input. Please provide a boolean value (True or False).")
        else:
            self.save_to_output = save_to_output

    def set_recursive(self, recursive):
        # Check if the provided value is a boolean
        if not isinstance(recursive, bool):
            print("Invalid input. Please provide a boolean value (True or False).")
        else:
            self.recursive = recursive

    def captions_to_metadata(self):
        start_time = time.time()  # Start timer

        with exiftool.ExifTool() as et:
            file_pattern = '**/*' if self.recursive else '*'
            for filename in glob.glob(os.path.join(self.input_dir, file_pattern), recursive=self.recursive):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                    print(f"Processing image: {filename}")  # Log the image currently being processed
                    try:
                        # Assume the caption file is in the same directory and has the same name as the image file
                        caption_file = filename.rsplit('.', 1)[0] + '.txt'
                        with open(caption_file, 'r', encoding='utf-8', errors='ignore') as f:
                            caption = self.sanitize_string(f.read().strip())

                        # Write the caption to the 'ImageDescription' field of the image's metadata
                        et.execute('-overwrite_original', '-ImageDescription={}'.format(caption), filename)
                        self.total_files_processed += 1

                        if self.save_to_output:
                            # Copy the image with updated metadata to the output directory
                            ds_metacaption_dir = os.path.join(self.output_dir, "DS_MetaCaption")
                            if not os.path.exists(ds_metacaption_dir):
                                os.makedirs(ds_metacaption_dir)
                            shutil.copy2(filename, ds_metacaption_dir)

                    except Exception as e:
                        self.failures += 1
                        print(colored(f"Error processing file {filename}: {str(e)}", 'red'))

        end_time = time.time()  # End timer
        avg_time = (end_time - start_time) / self.total_files_processed if self.total_files_processed > 0 else 0
        print(f"Average time per image: {avg_time:.2f} seconds")

    def metadata_to_captions(self):
        BATCH_SIZE = 50
        start_time = time.time()  # Start timer

        file_pattern = '**/*' if self.recursive else '*'
        image_files = [filename for filename in glob.glob(os.path.join(self.input_dir, file_pattern), recursive=self.recursive) 
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]

        with exiftool.ExifTool() as et:
            for i in range(0, len(image_files), BATCH_SIZE):
                batch_files = image_files[i: i + BATCH_SIZE]
                for filename in batch_files:
                    print(f"Processing image: {filename}")  # Log the image currently being processed
                    try:
                        # Get the 'ImageDescription' field from the image's metadata
                        metadata = json.loads(et.execute('-G', '-j', '-n', filename))
                        caption = self.sanitize_string(metadata[0]['EXIF:ImageDescription'])

                        if self.save_to_output:
                            # Write the caption to a text file in the output directory
                            ds_metacaption_dir = os.path.join(self.output_dir, "DS_MetaCaption")
                            if not os.path.exists(ds_metacaption_dir):
                                os.makedirs(ds_metacaption_dir)
                            caption_file = os.path.join(ds_metacaption_dir, os.path.basename(filename).rsplit('.', 1)[0] + '.txt')
                        else:
                            # Write the caption to a text file in the same directory as the image file
                            caption_file = filename.rsplit('.', 1)[0] + '.txt'

                        with open(caption_file, 'w', encoding='utf-8') as f:
                            f.write(caption)

                        self.total_files_processed += 1
                    except Exception as e:
                        self.failures += 1
                        print(colored(f"Error processing file {filename}: {str(e)}", 'red'))

        end_time = time.time()  # End timer
        avg_time = (end_time - start_time) / self.total_files_processed if self.total_files_processed > 0 else 0
        print(f"Average time per image: {avg_time:.2f} seconds")
    
    def convert(self):
        # Check the direction and call the corresponding method
        if self.direction == 'Caption to Metadata':
            self.captions_to_metadata()
        elif self.direction == 'Metadata to Caption':
            self.metadata_to_captions()
        else:
            print("Invalid direction. Please set the direction before converting.")

    def print_results(self):
        # Print the results after a conversion is done
        print(f'Total files processed: {self.total_files_processed}')
        print(f'Total failures: {self.failures}')

    def display_menu(self):
        # Update the display text according to user choices
        save_direction_text = self.direction
        save_to_output_text = 'ON' if self.save_to_output else 'OFF'
        recursive_text = 'ON' if self.recursive else 'OFF'

        print(colored(f'''
    Current Input Directory: {self.input_dir}
    Current Output Directory: {self.output_dir} (not inside input!)
    ┌──────────────────────────────────────────────────────────────────────────────┐
    |                          CAPTION <> METADATA MODULE                          |
    |------------------------------------------------------------------------------|
    |                                                                              |
    |              Settings                                                        | 
    |                                                                              |
    |          1 - Save Direction ({save_direction_text})                                   
    |          2 - Save to Output Folder ({save_to_output_text})                         
    |          3 - Recursive ({recursive_text})                                                 
    |                                                                              |
    └──────────────────────────────────────────────────────────────────────────────┘
    |      I - Set Input     O - Set Output     R - Run     X - Exit to Menu       |
    └──────────────────────────────────────────────────────────────────────────────┘
    ''', 'light_magenta'))

        print("Module converts metadata to and from as many formats allowable by pyexiftool")
        print("Save to Output Folder ON will save new items out to DS_MetaCaption folder in Output Directory")
        print("Recursive ON processes subfolders of the input directory\n")


    def convert_captions_and_metadata(self):
        total_captions = 0
        failures = 0
        # TODO: Implement the caption to metadata and metadata to caption conversion logic.
        # You'll need to use exiftool.ExifTool() and methods like get_metadata() and set_metadata().

    def run(self):
        while True:
            self.display_menu()
            choice = input("Enter your selection: ")

            if choice == '1':
                user_input = input("Would you like to save captions to image metadata (1) or extract metadata to .txt caption (2)?: ")
                self.set_direction('Caption to Metadata' if user_input == '1' else 'Metadata to Caption')
            elif choice == '2':
                user_input = input("Save captions to Output Directory?\n(only available with Metadata to Captions option, will be ignored otherwise) (Y/N)").lower()
                self.set_save_to_output(user_input in ['y', 'yes'])
            elif choice == '3':
                user_input = input("Process folders recursively? (Y/N)").lower()
                self.set_recursive(user_input in ['y', 'yes'])
            elif choice.lower() == 'i':
                new_input_dir = input("Change Input Directory: ")
                self.set_input_dir(new_input_dir)
            elif choice.lower() == 'o':
                new_output_dir = input("Change Output Directory: ")
                self.set_output_dir(new_output_dir)
            elif choice.lower() == 'r':
                confirm = input("WARNING: Module will save over existing captions and/or metadata description fields\nDataset Cleaner is experimental and only intended for backed up datasets\nUse only on backed up datasets and at your own risk\nRun the module? (Y/N) ")
                if confirm.lower() in ['y', 'yes']:
                    self.convert()
                    self.print_results()
            elif choice.lower() == 'x':
                break
            else:
                print("Invalid choice. Please choose a valid option or press 'x' to exit.")
