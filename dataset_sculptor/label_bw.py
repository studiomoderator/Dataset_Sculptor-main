import glob
import os
import cv2
from termcolor import colored
from torchvision.transforms.functional import InterpolationMode
from transformers import AutoProcessor, BlipForQuestionAnswering
import shutil

MODEL_NAME = "Salesforce/blip-vqa-base"

def query_blip(blip_model, processor, image, question, max_new_tokens=30):
    inputs = processor(images=image, text=question, return_tensors="pt")
    outputs = blip_model.generate(**inputs, max_new_tokens=max_new_tokens)
    return processor.decode(outputs[0], skip_special_tokens=True)

def move_to_quality_dir(file_path, output_dir):
    x_quality_dir = os.path.join(output_dir, "DS_Greyscale")

    destination_path = os.path.join(x_quality_dir, os.path.basename(file_path))
    if not os.path.exists(x_quality_dir):
        os.makedirs(x_quality_dir)

    shutil.move(file_path, destination_path)

    print(f"Moved file to: {destination_path}")

    return destination_path

def rename_and_update_file(base_path, options):
    base_file_name, file_extension = os.path.splitext(os.path.basename(base_path))
    new_file_name = f"{base_file_name}_BW{file_extension}"

    new_path = os.path.join(os.path.dirname(base_path), new_file_name)

    if options['rename']:
        os.rename(base_path, new_path)
        print(f"Renamed image file: {base_path} -> {new_path}")

    txt_file_name = os.path.splitext(base_path)[0] + ".txt"
    if os.path.isfile(txt_file_name) and options['update_caption']:
        new_txt_file_name = f"{base_file_name}_BW.txt"
        new_txt_path = os.path.join(os.path.dirname(txt_file_name), new_txt_file_name)

        with open(txt_file_name, 'r+') as f:
            existing_caption = f.read().rstrip('\n')
            # To append to the back of caption, change the line below to: content = f"{existing_caption} {options['update_text']}"
            content = f"{options['update_text']} {existing_caption}"
            f.seek(0)
            f.write(content)
            f.truncate()
        print(f"Updated content in: {txt_file_name}")

        os.rename(txt_file_name, new_txt_path)
        print(f"Renamed caption file: {txt_file_name} -> {new_txt_path}")

    if options['move_files']:
        new_path = move_to_quality_dir(new_path, options['output_dir'])
        if os.path.isfile(new_txt_path):
            new_txt_path = move_to_quality_dir(new_txt_path, options['output_dir'])

    return new_path

def label_bad_quality_images(input_dir, output_dir, options):
    print("Starting...")

    blip_model = BlipForQuestionAnswering.from_pretrained(MODEL_NAME)
    print("Model loaded.")

    processor = AutoProcessor.from_pretrained(MODEL_NAME)
    print("Processor loaded.")

    ext = ('.jpg', '.jpeg', '.png', '.webp', '.tif', '.tga', '.tiff', '.bmp', '.gif',
           '.JPG', '.JPEG', '.PNG', '.WEBP', '.TIF', '.TGA', '.TIFF', '.BMP', '.GIF')
    files_processed = 0

    # Define a dictionary to track the counts of different responses
    answer_counts = {}

    for idx, img_file_name in enumerate(glob.glob(os.path.join(input_dir, "**", "*.*"), recursive=True)):
        if img_file_name.endswith(ext):
            print(f"Processing image: {img_file_name}")

            try:
                image = cv2.imread(img_file_name)
                if image is None:
                    print(f"Failed to read image: {img_file_name}")
                    continue

                if image.shape[2] == 1:
                    image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
                elif image.shape[2] == 4:
                    image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)

                answer = query_blip(blip_model, processor, image, "Is the image in color or black and white?")
                print(f"BLIP's answer: {answer}")

                # Update the counts of different responses
                if answer.lower() in answer_counts:
                    answer_counts[answer.lower()] += 1
                else:
                    answer_counts[answer.lower()] = 1

                if "black and white" in answer.lower():
                    answer_quality = query_blip(blip_model, processor, image, "Can you describe the quality of the photo?")
                    print(f"BLIP's answer: {answer_quality}")
                    options['update_text'] = f"A {answer_quality} image of"
                    img_file_name = rename_and_update_file(img_file_name, options)

                files_processed += 1

            except Exception as e:
                print(f"Failed to process image: {img_file_name}. Error: {e}")
                continue

    print(f"Processed {files_processed} files.")
    print(f"Answer counts: {answer_counts}")  # Print the counts of different answers

def run_advanced_greyscale(input_dir, output_dir):
    options = {
        'rename': False,
        'update_caption': False,
        'move_files': False,
        'output_dir': output_dir,
        'update_text': ""
    }

    while True:
        print(colored(f'''
        
                      
                 ___      __   ___  __           ___      ___           
                |__  \_/ |__) |__  |__) |  |\/| |__  |\ |  |   /\  |    
                |___ / \ |    |___ |  \ |  |  | |___ | \|  |  /~~\ |___ 
        ''', 'cyan'))                                                
        print(colored(f'''
        Current Input Directory: {input_dir}
        Current Output Directory: {output_dir}
    ┌──────────────────────────────────────────────────────────────────────────────┐
    |                    ADVANCED GREYSCALE DETECTION MODULE                       |
    |------------------------------------------------------------------------------|
    |                                                                              |
    |              Settings                                                        | 
    |                                                                              |
    |          1 - Label Filenames with _BW ({'ON' if options['rename'] else 'OFF'})
    |          2 - Blip quality description to caption ({'ON' if options['update_caption'] else 'OFF'})                                             
    |          3 - Move Low Quality to Output/DS_LowQuality ({'ON' if options['move_files'] else 'OFF'})                                                 
    |                                                                              |
    └──────────────────────────────────────────────────────────────────────────────┘
    |          I - Set Input         R - Run         X - Exit to Menu              |
    └──────────────────────────────────────────────────────────────────────────────┘
    ▓▓▓▓▓▓▓▓▓▓██████████▓▓▓▓▓▓▓▓▓▓██████████▓▓▓▓▓▓▓▓▓▓██████████▓▓▓▓▓▓▓▓▓▓██████████

    Module uses machine vision to analyze images to find black and white images
    Options label filenames, add quality descriptions to the caption specific to the image, 
    or move files to Output Directory DS_Greyscale

    EXPERIMENTAL -- Basic BW tool still has better results on broader datasets
    BlipQuestions can be tweaked in .py files to experiment

    ''', 'light_grey', 'on_grey'))

        choice = input("\nEnter your selection: ").strip().upper()

        if choice == '1':
            user_response = input("Would you like to add a label to the filenames of black and white images? (Y/N) ").strip().upper()
            if user_response == 'Y':
                options['rename'] = True
            elif user_response == 'N':
                options['rename'] = False
            else:
                print(colored("Invalid input. Please select Y or N.", "red"))

        elif choice == '2':
            user_response = input("Would you like to add a description of the quality to the caption? (Y/N) ").strip().upper()
            if user_response == 'Y':
                options['update_caption'] = True
            elif user_response == 'N':
                options['update_caption'] = False
            else:
                print(colored("Invalid input. Please select Y or N.", "red"))

        elif choice == '3':
            user_response = input("Move the images to Output Directory? (Y/N) ").strip().upper()
            if user_response == 'Y':
                options['move_files'] = True
            elif user_response == 'N':
                options['move_files'] = False
            else:
                print(colored("Invalid input. Please select Y or N.", "red"))

        elif choice == 'I':
            input_dir = input("Enter new Input Directory path: ").strip()
            if not os.path.exists(input_dir):
                print(colored("The provided input directory doesn't exist. Please try again.", "red"))

        elif choice == 'R':
            warning_message = """
            WARNING: Module will alter files based on quality
            Dataset Sculptor is experimental and only intended for backed up datasets
            Use at your own risk
            Run the module? (Y/N) 
            """
            user_response = input(warning_message).strip().upper()
            if user_response in ['Y', 'YES']:
                try:
                    label_bad_quality_images(input_dir, output_dir, options)
                except Exception as e:
                    print(colored(f"An error occurred while processing: {e}", "red"))
            else:
                print("Module execution aborted.")


        elif choice == 'X':
            print("Exiting to main menu.")
            break

        else:
            print(colored("Invalid selection. Please try again.", "red"))


