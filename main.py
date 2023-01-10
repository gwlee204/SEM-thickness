"""
MIT License

Copyright (c) 2023 Geon-woo Lee

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import parmap
import multiprocessing

import os
import cv2
import numpy as np


NUM_CORES = multiprocessing.cpu_count()


def init():
    if 'data' not in os.listdir('./'):
        os.mkdir('./data')


def set_calibration():
    """
    Set calibration value

    1. Get number of pixel in SEM image's scale bar.
    2. Get actual length of scale bar.
    3. Calculate each pixel's actual length.
    """
    global CALIBRATION_VALUE

    pixel = int(input('calibration(pixel) : '))
    length = int(input('calibration(um) : '))
    CALIBRATION_VALUE = length / pixel

    print(f'calibration : {CALIBRATION_VALUE} um/pixel')


def select_files():
    """
    Select SEM image files with gui.

    Returns:
        list: list of file paths.
    """
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    
    available_file_type = '.jpg .jpeg .png .tif .tiff'
    files = filedialog.askopenfilenames(
        filetypes=((f'img files({available_file_type})', available_file_type),), initialdir='./data'
    )

    return files


def find_length_inline(line: list):
    """
    Calculate actual length of a single line.

    Args:
        line (list): BGR data data of line.

    Returns:
        float: If detected_point is larger than 1, return length between start point and end point.
    """
    detected_point = []
    for point in range(0, len(line)):
        if abs(np.mean(line[point]) - line[point][2]) > 10:
            detected_point.append(point)

    if len(detected_point) > 2:
        return(calibration(detected_point[-1] - detected_point[0]))
    else:
        return None


def thickness_analyze(path: str):
    """
    Find every vertical thickness in image.\n
    Base image must 8bit-grayscale image,
    and target region's color must red(RGB: 255, 0, 0)

    Args:
        path (str): Image path.

    Returns:
        list: List of thicknesses of image's every vertical thickness.
    """
    print(path)

    img = load_img(path)

    raw_results = parmap.map(find_length_inline, img, pm_pbar=True, pm_processes=NUM_CORES-2)
    
    result = remove_none_in_list(raw_results)

    return result


def load_img(path: str):
    """
    Load image file with input path.

    Args:
        path (str): Absolute path of image.

    Returns:
        image matrix : Loaded image's BGR matrix.
    """
    img = cv2.imread(path)
    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    return img


def remove_none_in_list(data: list):
    """
    Remove None or NaN in input data.

    Args:
        data (list): Raw list with numbers.

    Returns:
        list: None and NaN removed list.
    """
    res = []
    for point in data:
        if point != None and point != np.nan:
            res.append(point)
    return res
    

def calibration(data: int|float):
    """
    Calibration with CALIBRATION_VALUE.

    Args:
        data (int | float): Raw data that want to calibrate.

    Returns:
        float: Calibrated value
    """
    return data * CALIBRATION_VALUE


if __name__ == '__main__':
    init()
    set_calibration()
    img_files = select_files()
    
    for img_path in img_files:
        res = thickness_analyze(img_path)
        mean_thickness = np.mean(res)
        std_thickness = np.std(res)
        print(f'average thickness : {mean_thickness} um, standard deviation : {std_thickness} um')
    
    os.system('pause')
