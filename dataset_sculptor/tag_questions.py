import glob
import os
import cv2
import argparse
from termcolor import colored
from torchvision.transforms.functional import InterpolationMode
from transformers import AutoProcessor, BlipForQuestionAnswering
import shutil
import random
import traceback

MODEL_NAME = "Salesforce/blip-vqa-base"

def query_blip(blip_model, processor, image, question, max_new_tokens=30):
    inputs = processor(images=image, text=question, return_tensors="pt")
    outputs = blip_model.generate(**inputs, max_new_tokens=max_new_tokens)
    return processor.decode(outputs[0], skip_special_tokens=True)

def move_to_quality_dir(file_path, output_dir):
    ds_question_dir = os.path.join(output_dir, "DS_Question")

    if not os.path.exists(ds_question_dir):
        os.makedirs(ds_question_dir)

    destination_path = os.path.join(ds_question_dir, os.path.basename(file_path))
    shutil.move(file_path, destination_path)

    print(f"Moved file to: {destination_path}")
    return destination_path

def rename_and_update_file(base_path, options, prefix='', update_text=''):
    base_file_name, file_extension = os.path.splitext(os.path.basename(base_path))
    if options['rename_position'] == 'start':
        new_file_name = f"{prefix}{base_file_name}{file_extension}"
    else:
        new_file_name = f"{base_file_name}{prefix}{file_extension}"
    
    new_path = os.path.join(os.path.dirname(base_path), new_file_name)
    if options['rename']:
        os.rename(base_path, new_path)
        print(f"Renamed image file: {base_path} -> {new_path}")

    txt_file_name = os.path.splitext(base_path)[0] + ".txt"
    if os.path.isfile(txt_file_name) and options['update_caption']:
        new_txt_file_name = f"{os.path.splitext(new_file_name)[0]}.txt"
        new_txt_path = os.path.join(os.path.dirname(txt_file_name), new_txt_file_name)

        with open(txt_file_name, 'r+') as f:
            existing_caption = f.read().rstrip('\n')
            lines = existing_caption.split('\n')
            separator = '\n' if options['newline_caption'] else ' '

            if options['update_caption_position'] == 'random':
                random_index = random.randint(0, len(lines))
                lines.insert(random_index, update_text)
                content = separator.join(lines)
            elif options['update_caption_position'] == 'before':
                content = f"{update_text}{separator}{existing_caption}"
            else:  # 'after'
                content = f"{existing_caption}{separator}{update_text}"

            f.seek(0)
            f.write(content)
            f.truncate()
        print(f"Updated content in: {txt_file_name}")

        os.rename(txt_file_name, new_txt_path)
        print(f"Renamed caption file: {txt_file_name} -> {new_txt_path}")

        # Move files after rename
        if options['move_files']:
            new_txt_path = move_to_quality_dir(new_txt_path, options['output_dir'])
            new_path = move_to_quality_dir(new_path, options['output_dir'])
    
    return new_path

def label_bad_quality_images(input_dir, output_dir, options):
    if 'output_dir' not in options:
        print("Error: 'output_dir' key missing in options!")
        return
    options['output_dir'] = output_dir
    print("Starting...")

    blip_model = BlipForQuestionAnswering.from_pretrained(MODEL_NAME)
    print("Model loaded.")
    processor = AutoProcessor.from_pretrained(MODEL_NAME)
    print("Processor loaded.")
    
    ext = ('.jpg', '.jpeg', '.png', '.webp', '.tif', '.tga', '.tiff', '.bmp', '.gif',
           '.JPG', '.JPEG', '.PNG', '.WEBP', '.TIF', '.TGA', '.TIFF', '.BMP', '.GIF')
    files_processed = 0
    answer_counts = {}

    for idx, img_file_name in enumerate(glob.glob(os.path.join(input_dir, "**", "*.*"), recursive=True)):
        print(f"Checking file: {img_file_name}")
        if img_file_name.endswith(ext):
            print(f"Processing image: {img_file_name}")
            try:
                # Assuming you've loaded the image and stored it in the variable named 'image'
                
                image = cv2.imread(img_file_name)  # Load the image using OpenCV
                answer_quality = query_blip(blip_model, processor, image, options['blip_question1'])

                
                if answer_quality.lower() in answer_counts:
                    answer_counts[answer_quality.lower()] += 1
                else:
                    answer_counts[answer_quality.lower()] = 1
                    
                if "yes" in answer_quality.lower() or "true" in answer_quality.lower():
                    
                    # Update the file's name with the user-specified label (from prompt 3)
                    new_img_file_name = rename_and_update_file(img_file_name, options, prefix=options['rename_label'])
                    
                    # Get the answer to the second question and update the caption with this answer
                    answer_caption = query_blip(blip_model, processor, image, options['blip_question2'])
                    
                    # Check if there's a corresponding txt file and update its content
                    txt_file_name = os.path.splitext(new_img_file_name)[0] + ".txt"
                    if os.path.isfile(txt_file_name):
                        with open(txt_file_name, 'r+') as f:
                            existing_caption = f.read().rstrip('\n')
                            separator = '\n' if options['newline_caption'] else ' '
                            
                            if options['update_caption_position'] == 'random':
                                lines = existing_caption.split('\n')
                                random_index = random.randint(0, len(lines))
                                lines.insert(random_index, answer_caption)
                                content = separator.join(lines)
                            elif options['update_caption_position'] == 'before':
                                content = f"{answer_caption}{separator}{existing_caption}"
                            else:  # 'after'
                                content = f"{existing_caption}{separator}{answer_caption}"

                            f.seek(0)
                            f.write(content)
                            f.truncate()
                        print(f"Updated content in: {txt_file_name}")
                        
                files_processed += 1

            except Exception as e:
                print(f"Failed to process image: {img_file_name}. Error: {e}")
                traceback.print_exc()
                continue

        print(f"Processed {files_processed} files.")
        print(f"Answer counts: {answer_counts}")

def run(input_dir, output_dir):
    while True:
        print(colored(f'''
                   ___      __   ___  __           ___      ___           
                  |__  \_/ |__) |__  |__) |  |\/| |__  |\ |  |   /\  |    
                  |___ / \ |    |___ |  \ |  |  | |___ | \|  |  /~~\ |___ 
        ''', 'light_yellow'))                                              
        print(colored(f'''
        Current Input Directory: {input_dir}
        Current Output Directory: {output_dir}
     ┌──────────────────────────────────────────────────────────────────────────────┐
     |                           IMAGE QUESTIONING MODULE                           |
     |------------------------------------------------------------------------------|
     |                                                                              |
     |            Prompt List Order (linear sequence on Run, not interactive)       | 
     |                                                                              |
     |        1 - Rename with label if BlipQuestion1 is TRUE (Y, N)                 |
     |        2 - Add label at beginning (1) or end (2) of the filename?            |                                         
     |        3 - Please enter the label for the filename:                          | 
     |        4 - Append captions with answer to BlipQuestion2? (Y, N):             |
     |        5 - Caption before (1), after (2), or random position (3)?            |                                         
     |        6 - New line for the additional caption? (Y, N)                       |  
     |        7 - Move images and text files to Output folder (Y, N)                | 
     |        8 - First question to ask about image                                 | 
     |        9 - Second question to ask of image                                   |                        
     |                                                                              |
     └──────────────────────────────────────────────────────────────────────────────┘
     |      I - Set input     O - Set Output     R - Run     X - Exit to Menu       |
     └──────────────────────────────────────────────────────────────────────────────┘

		Notes:
	1 - 5 	self-explanatory
	6 - 	Adds a new line before or after existing caption for use with trainers 
		that accept multiple caption lines. Recommended off unless your questions
		are able to pull longer answers from BlipQuestion
	7 -     Moves images to new output subfolder DS_Question
	8 - 	First question to ask about the images, should be binary Yes or No
	9 - 	Second question to ask about the images, should be open-ended
	
    ''', 'light_green'))

        choice = input("Enter one of the options from system menu (I, O, R, X): ").upper()

        if choice == 'I':
            input_dir = input("Set new input directory: ")
        elif choice == 'O':
            output_dir = input("Set new output directory: ")
        elif choice == 'R':
            break
        elif choice == 'X':
            return

    # Capture the rest of the user inputs
    rename_files = input("Rename with label if BlipQuestion1 answer is TRUE? (Y, N): ")
    rename_files = rename_files.upper() == 'Y'
    rename_position = ''
    rename_label = ''
    if rename_files:
        rename_position = input("Add label at the beginning (1) or the end (2) of the filename? ")
        if rename_position == '1':
            rename_position = 'start'
        elif rename_position == '2':
            rename_position = 'end'
        rename_label = input("Please enter the label for the file: ")

    update_caption = input("Append captions with answer to follow up BlipQuestion2? (Y, N): ")
    update_caption = update_caption.upper() == 'Y'
    if update_caption:
        update_caption_position = input("Should the caption go before (1), after (2), or at a random position (3)? ")
        if update_caption_position == '1':
            update_caption_position = 'before'
        elif update_caption_position == '2':
            update_caption_position = 'after'
        elif update_caption_position == '3':
            update_caption_position = 'random'
    else:
        update_caption_position = None

    newline_caption = input("New line for the additional caption? (Y, N): ")
    newline_caption = newline_caption.upper() == 'Y'

    move_files = input("Move images and text files to Output folder (Y, N): ")
    move_files = move_files.upper() == 'Y'

    blip_question1 = input("Please enter BlipQuestion1: ")
    blip_question2 = input("Please enter BlipQuestion2 (if BlipQuestion1 answer is TRUE): ")
    blip_question2 = blip_question2 if blip_question2 else None

    options = {
        'rename': rename_files,
        'rename_position': rename_position,
        'rename_label': rename_label,
        'update_caption': update_caption,
        'update_caption_position': update_caption_position,
        'newline_caption': newline_caption,
        'move_files': move_files,
        'blip_question1': blip_question1,
        'blip_question2': blip_question2,
        'output_dir': output_dir, 
        'input_dir': input_dir 
}

    label_bad_quality_images(input_dir, output_dir, options)



if __name__ == '__main__':
    run('default_input_dir', 'default_output_dir')  # These can be changed to your default directories.