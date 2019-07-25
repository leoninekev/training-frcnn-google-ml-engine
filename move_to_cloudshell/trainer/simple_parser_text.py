from __future__ import absolute_import

import cv2
from tensorflow.python.lib.io import file_io
import io
import numpy as np

from PIL import Image


def new_open(name, mode, buffering=-1):
    return file_io.FileIO(name, mode)


def url2img(uri):  # function compliant to loading gs:// url images
    file = new_open(uri, mode='rb')
    file = file.read()
    img = Image.open(io.BytesIO(file)).convert('RGB')
    return np.asarray(img)


def get_data(input_path):
	found_bg = False
	all_imgs = {}
	classes_count = {}
	class_mapping = {}
	
	with new_open(input_path, mode='r') as f:  # holds gs://annotations.txt
		print('Parsing annotation files')
		for line in f:
			line_split = line.strip().split(',')
			(filename, x1, y1, x2, y2, class_name) = line_split

			if class_name not in classes_count:
				classes_count[class_name] = 1
			else:
				classes_count[class_name] += 1
								
			if class_name not in class_mapping:
				if class_name == 'bg' and found_bg == False:
					print('Found class name with special name bg. Will be treated as a background region (this is usually for hard negative mining).')
					found_bg = True
				class_mapping[class_name] = len(class_mapping)

			if filename not in all_imgs:
				all_imgs[filename] = {}

				img = url2img(filename)
				#img = cv2.imread(filename)
				(rows, cols) = img.shape[:2]
				all_imgs[filename]['filepath'] = filename
				all_imgs[filename]['width'] = cols
				all_imgs[filename]['height'] = rows
				all_imgs[filename]['bboxes'] = []
				if np.random.randint(0, 6) > 0:
					all_imgs[filename]['imageset'] = 'trainval'
				else:
					all_imgs[filename]['imageset'] = 'test'
			
			all_imgs[filename]['bboxes'].append({'class': class_name, 'x1': int(x1), 'x2': int(x2), 'y1': int(y1), 'y2': int(y2)})

		all_data = []
		for key in all_imgs:
			all_data.append(all_imgs[key])

        # make sure the bg class is last in the list
		if found_bg:
			if class_mapping['bg'] != len(class_mapping) - 1:
				key_to_switch = [key for key in class_mapping.keys() if class_mapping[key] == len(class_mapping)-1][0]
				val_to_switch = class_mapping['bg']
				class_mapping['bg'] = len(class_mapping) - 1
				class_mapping[key_to_switch] = val_to_switch

		return all_data, classes_count, class_mapping
