
# Dataset Sculptor 

<img src="https://github.com/studiomoderator/dataset_sculptor/assets/139658962/28ec2453-4deb-4451-b6aa-85891fbf80f0" alt="drawing" width="500"/>

<br> 

Dataset Sculptor provides a suite of tools tailored for researchers and enthusiasts in the realm of machine learning, specifically for image diffusion training. With the increasing importance of clean and structured datasets, this tool aims to streamline preprocessing tasks, ensuring your data is primed for optimal training performance. Each module offers functions to enhance and refine your datasets, from image quality control to metadata management.

## Table of Contents
- [Features](#features)
  - [Delete Small Images and Orphan Captions](#delete-small-images-and-orphan-captions)
  - [Reduce Image Size](#reduce-image-size)
  - [Convert to .jpg or .png](#convert-to-jpg-or-png)
  - [Captions > Metadata | Metadata > Captions](#captions-metadata-metadata-captions)
  - [Tag / Move Black and White Image](#tag-move-black-and-white-image)
  - [Move Image-Caption Pairs Based on Filename String](#move-image-caption-pairs-based-on-filename-string)
  - [Advanced Quality Analysis (Tag / Caption / Move)](#advanced-quality-analysis)
  - [Next-Gen Black and White Filter (Tag / Caption / Move)](#next-gen-black-and-white-filter)
  - [Tags from BlipQuestions (Experimental)](#tags-from-blipquestions)
  - [Autocaption Plus (In Development)](#autocaption-plus)
- [Installation](#installation)
- [Libraries and Tools Used](#libraries-and-tools-used)

## Features

#### Delete Small Images and Orphan Captions
This module scans the specified directory for images and captions. Any images that are smaller than the specified length on either dimension are deleted. If the option to delete orphan captions is activated, captions (in the form of .txt files) that don't have corresponding images are also removed. 
#### Reduce Image Size
This module provides tools to resize images that exceed a specified maximum dimension while preserving their aspect ratios. Users can choose whether to save the resized images to a separate output directory or overwrite the originals. The module supports multiple configurations, including processing images in subdirectories recursively and the option to retain the original images alongside the resized ones.
#### Convert to .jpg or .png
The ImageConverter module facilitates the conversion of images to a user-specified file format from a wide range of supported formats. Users can opt whether to retain the original images after conversion, and the converted images can be saved either in the same directory, overwriting the originals, or in a separate output directory.

#### Captions > Metadata | Metadata > Captions
The MetadataCaptionConverter module enables the bidirectional conversion between image metadata and captions. Users can either embed captions from text files into an image's metadata or extract metadata descriptions to generate caption text files. 

#### Tag / Move Black and White Image
The BWImageMenu module identifies and manages black and white images based on a mean squared error threshold. It offers options to rename these images, append labels to associated captions, and either copy, move, or leave the images in their original locations. 

#### Move Image-Caption Pairs Based on Filename String
The MoveString class enables users to either move or copy files based on a filename substring. Through an interactive menu, users specify search criteria, choose between copying or moving files, and decide if subfolders should be processed. 

#### Advanced Quality Analysis 
The "Advanced Quality Detection Module" uses the BlipForQuestionAnswering machine vision model to evaluate image quality. Users interact with a menu to choose actions on low-quality images, such as renaming files, adding quality descriptions to captions, or moving images to a designated directory.

#### Next-Gen Black and White Filter 
This script employs the BlipForQuestionAnswering machine vision model to identify black and white images within a dataset. Based on user-selected options, the program can rename these images, append descriptive captions about their quality, or move them to a specific "DS_Greyscale" directory. 

#### Tags from BlipQuestions (Experimental)
This module uses the BlipForQuestionAnswering machine vision model to interrogate images based on two user-specified questions, with the primary question expecting a binary (Yes or No) response. If the answer to the first question is affirmative, the images can be optionally renamed, their captions amended based on the answer to the secondary question, and then moved to a dedicated "DS_Question" subfolder in the output directory. Users interact with a text-based menu system to customize how images are processed and to specify the questions posed to the model.

#### Autocaption Plus (In Development)
A placeholder for an upcoming feature aiming to provide advanced auto-captioning capabilities.

## Installation

1. **Setting Up the Virtual Environment**  
   Navigate to the `Dataset_Sculptor-main` directory in your command prompt and set up a virtual environment:
   ```
   python -m venv venv
   ```
   ```
   venv\Scripts\activate.bat
   ```

3. **Install EXIFTOOL**  
   Download the standalone .exe (without the need for Perl) and add it to your Windows PATH:
   - [EXIFTOOL Download](https://exiftool.org/install.html)

4. **Install Necessary Dependencies**  
   Use pip to install the required packages and dependencies:
   ```
   pip install -r requirements.txt
   ```
   ```
   pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 --extra-index-url https://download.pytorch.org/whl/cu113
   ```
   ```
   git clone https://github.com/salesforce/BLIP scripts/BLIP
   ```

5. **Activate Virtual Environment on Subsequent Uses**  
   Every time you open the command prompt, ensure the virtual environment is activated:
   ```
   venv\Scripts\activate.bat
   ```

6. **Running the Tool**  
   Execute the script, specifying the input and output directories. Here's an example:
   ```
   python dataset_sculptor.py --input_dir C:/Training_DS/Input --output_dir C:/Training_DS/Output
   ```

## Libraries and Tools Used

- **Python Standard Library**: Essential for basic operations and file management; key modules include `glob`, `os`, `argparse`, `shutil`, `random`, and `traceback`.
- **OpenCV (cv2)**: A comprehensive library used for computer vision tasks, enabling image processing and transformations.
- **HuggingFace's Transformers**: Provides a vast array of NLP models and utilities, including Salesforce's **Blip** for Vision Question Answering tasks.
- **Torchvision (from PyTorch)**: Used for specific vision utilities and transformations.
- **termcolor**: Used for colored terminal outputs, enhancing user interactivity.
- **exiftool**: A tool crucial for reading, writing, and editing meta information in files, especially for handling image metadata.
- **Salesforce's Blip**: A model from the HuggingFace's Transformers library, specifically used for question-answering tasks related to images.

## Additional Documentation

**- Screenshots**
https://github.com/studiomoderator/Dataset_Sculptor-main/blob/main/screenshots.md

**- Video intro**
https://www.youtube.com/watch?v=KgSQK7oN_rQ

**- Video walkthrough**
https://www.youtube.com/watch?v=9Ad4VTWi5ns



