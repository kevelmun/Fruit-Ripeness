import glob
import open3d as o3d
from POP2.extract_image_pcd import point_cloud_to_image
from POP2.util import *
from POP2.capture3d import *
import os

if __name__ == "__main__":

    try:
        categorias = ["mango"]
        for cat in categorias:
            input_folder = f"./data/POP2/{cat}/pcd/"  
            output_folder = f"./data/POP2/{cat}/color/"
            print(f"Input folder: {input_folder}")
            print(f"Output folder: {output_folder}")
            process_input_folder(input_folder, output_folder)
    except Exception as e:
        print(f"An error occurred: {e}")