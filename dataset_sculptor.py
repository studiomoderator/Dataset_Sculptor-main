import argparse
from termcolor import colored
from dataset_sculptor import delete_small_images
from dataset_sculptor import reduce_img
from dataset_sculptor import image_converter
from dataset_sculptor import caption_to_metadata
from dataset_sculptor import move_bw_images
from dataset_sculptor import move_string
from dataset_sculptor import advanced_quality
from dataset_sculptor import label_bw
from dataset_sculptor import tag_questions
from dataset_sculptor import autocaption_plus
from dataset_sculptor.move_bw_images import main_execution_loop
from dataset_sculptor.move_string import MoveString



def display_menu():
    print(colored('''
                             		
      __       ___       __   ___ ___     __   __             __  ___  __   __  
     |  \  /\   |   /\  /__` |__   |     /__` /  ` |  | |    |__)  |  /  \ |__) 
     |__/ /~~\  |  /~~\ .__/ |___  |     .__/ \__, \__/ |___ |     |  \__/ |  \  0.9                                                                       
                                                                       
     ┌──────────────────────────────────────────────────────────────────────────────┐
     |                        BASIC TOOLS | PYTHON (Fast)                           |
     |------------------------------------------------------------------------------|
     |          1 - Delete Small Images and Orphan Captions                         |
     |          2 - Reduce Image Size                                               |
     |          3 - Convert to .jpg or .png                                         |
     |          4 - Captions > Metadata | Metadata > Captions                       |
     |          5 - Tag / Move Black and White Image                                |
     |          6 - Move Image-Caption Pairs Based on Filename String               |
     |                                                                              |
     ┌──────────────────────────────────────────────────────────────────────────────┐
     |             ADVANCED TOOLS | BLIP MACHINE VISION (GPU-intensive)             |
     |------------------------------------------------------------------------------|
     |          7 - Advanced Quality Analysis (Tag / Caption / Move)                |
     |          8 - Next-Gen Black and White Filter (Tag / Caption / Move)          |
     |          9 - Tags from BlipQuestions (Experimental)                          |
     |          0 - Autocaption Plus (In Development)                               |
     |                                                                              |
     ┌──────────────────────────────────────────────────────────────────────────────┐
     └──────────────────────────────────────────────────────────────────────────────┘
     |          I - Set input      O - Set Output       X - Exit to Prompt          |
     └──────────────────────────────────────────────────────────────────────────────┘
	''', 'white'))
    print(colored(''' 
                        WARNING: Dataset Sculptor is experimental
              Test thoroughly on smaller trial folders and backup your dataset
    ''', 'red'))

def process_choice(choice, input_dir, output_dir):
    if choice == '1':
        small_image_deleter = delete_small_images.DeleteSmallImages()
        small_image_deleter.set_input_dir(input_dir)
        small_image_deleter.run()
    elif choice == '2':
        image_resizer = reduce_img.ReduceImage()
        image_resizer.set_input_dir(input_dir)
        image_resizer.set_output_dir(output_dir)  # only needed if you want to output to a different directory
        image_resizer.run()
    elif choice == '3':
        img_converter = image_converter.ImageConverter(input_dir, output_dir)
        img_converter.run()
    elif choice == '4':
        metadata_converter = caption_to_metadata.MetadataCaptionConverter(input_dir, output_dir)
        metadata_converter.run()
    elif choice == '5':
        main_execution_loop(input_dir, output_dir)
    elif choice == '6':
        mover = MoveString()
        mover.set_input_dir(input_dir)
        mover.set_output_dir(output_dir)
        mover.run()
    elif choice == '7':
        advanced_quality.run_advanced_quality(input_dir, output_dir)
    elif choice == '8':
        label_bw.run_advanced_greyscale(input_dir, output_dir)
    elif choice == '9':
        tag_questions.run(input_dir, output_dir)
    elif choice == '0':
        autocaption_plus.run(input_dir, output_dir)
    elif choice.lower() == 'i':
        input_dir = input("Enter new input directory: ")
    elif choice.lower() == 'o':
        output_dir = input("Enter new output directory: ")
    elif choice.lower() == 'x':
        return None, None

    return input_dir, output_dir

def main():
    parser = argparse.ArgumentParser(description='Dataset Sculptor')
    parser.add_argument('--input_dir', type=str, default=None, help='Input directory')
    parser.add_argument('--output_dir', type=str, default=None, help='Output directory')

    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    if not input_dir:
        input_dir = input("Enter input directory: ")
    if not output_dir:
        output_dir = input("Enter output directory: ")

    while True:
        display_menu()
        choice = input("Choose an option (0-9, I, O) or press 'X' to exit: ")

        input_dir, output_dir = process_choice(choice, input_dir, output_dir)

        if input_dir is None and output_dir is None:
            break

if __name__ == "__main__":
    main()
