import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET
import time

from optparse import OptionParser

parser= OptionParser()
parser.add_option("-s", "--source", dest="image_dir",help="Path to directory containing images & xmls locally", default= os.path.join(os.getcwd(), 'food_data'))#default assumes images are in folder named food_data
parser.add_option("-b", "--bucket_path", dest="gcloud_bucket",help="gCloud Path to directory containing images")
parser.add_option("-d","--destination", dest="save_to", help= "Path to save annotation txt file", default = os.path.join(os.getcwd(),'annotations.txt'))

(options, args) = parser.parse_args()

def xml_to_df(path, subdirectories = True):
    xml_list = []
    if subdirectories:
        classes = os.listdir(path)
        for cls in classes:
            for xml_file in glob.glob(os.path.join(path, cls) + '/*.xml'):
                tree = ET.parse(xml_file)
                root = tree.getroot()
                for member in root.findall('object'):
                    value = (root.find('filename').text,
                            int(root.find('size')[0].text),
                            int(root.find('size')[1].text),
                            member[0].text,
                            int(member[4][0].text),
                            int(member[4][1].text),
                            int(member[4][2].text),
                            int(member[4][3].text)
                            )
                    xml_list.append(value)
        column_name = ['filename', 'width', 'height', 'classes', 'xmin', 'ymin', 'xmax', 'ymax']
        xml_df = pd.DataFrame(xml_list, columns=column_name)
    else:
        for xml_file in glob.glob(path + '/*.xml'):
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for member in root.findall('object'):
                value = (root.find('filename').text,
                        int(root.find('size')[0].text),
                        int(root.find('size')[1].text),
                        member[0].text,
                        int(member[4][0].text),
                        int(member[4][1].text),
                        int(member[4][2].text),
                        int(member[4][3].text)
                        )
                xml_list.append(value)
        column_name = ['filename', 'width', 'height', 'classes', 'xmin', 'ymin', 'xmax', 'ymax']
        xml_df = pd.DataFrame(xml_list, columns=column_name)

    return xml_df


def main(src_path, gcloud_path, dest_path):
    cols_req = ['filename','xmin', 'ymin', 'xmax', 'ymax','classes']
    if all([fil.endswith(('.jpg','.xml')) for fil in os.listdir(src_path)]):#True, When all images are stored in single directory
        print('Single directory cotains all images')
        xml_df =xml_to_df(src_path, subdirectories= False)
        xml_df['filename'] = xml_df['filename'].apply(lambda x: os.path.join(gcloud_path, x))#appending gcloud_bucket path to names
    else:#True, When images are stored in various respective classes subdirectory
        print('Multiple subdirectories contain images')
        xml_df= xml_to_df(src_path)
        xml_df['filename'] = xml_df[[cols_req[-1], 'filename']].apply(lambda x: os.path.join(gcloud_path,'/'.join(x.astype(str))),axis=1)
    df_txt = pd.DataFrame()    
    df_txt = xml_df[cols_req].apply(lambda x : ','.join(x.astype(str)),axis=1)
    
    df_txt.to_csv(dest_path, header= None, index=None,sep=' ')
    #Note: the text file saved is now rectified within code itself, by manually editing select xmls containing wrong image_names prior to running this script.
    print('\nSuccessfully written all xmls to txt.')

if __name__=="__main__":
    tick = time.time()
    src_path = options.image_dir
    gcloud_path = options.gcloud_bucket#if gcloud path is not give, following expression overwrites this one
    if not options.gcloud_bucket:
        print('Enter a VALID gcloud bucket path to directory containing images! Appending a dummy path for now. . .')
        gcloud_path= 'gs://your_gcloud_bucket_name/food_data/'
    dest_path=options.save_to
    main(src_path, gcloud_path, dest_path)
    print('Annotation file created at: {}\ntime elapsed: {}'.format(dest_path, time.time()-tick))
