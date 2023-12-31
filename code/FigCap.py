"""
main code page
structure (xpdf_process):
1. Read pdfs from input folder
2. Figure and caption pair detection
    2.1. graphical content detection
    2.2 page segmentation
    2.3 figure detetion
    2.4 caption association

3. Mess up pdf processing


Writen by Pengyuan Li

Start from 19/10/2017
1.0 version 28/02/2018

"""

import os
import renderer
from xpdf_process import figures_captions_list
import subprocess
import os
import time
import uuid


def extract_figure_and_caption(input_path, output_path):
    xpdf_path = output_path +'/xpdf/'  
    log_file = output_path + '/log.text'
    f_log = open(log_file, 'w') 
    if not os.path.isdir(xpdf_path):
        os.mkdir(xpdf_path)
# Read each files in the input path
    all_data=[]
    pdf_files = [pdf for pdf in os.listdir(input_path) if pdf.endswith('.pdf') and not pdf.startswith('._')]
    pdf_files.sort(key=lambda x: int(x.split("_")[1].split(".")[0]))  
    for pdf in pdf_files:
        print(pdf)
        data = {}
        images = renderer.render_pdf((input_path + '/' + pdf), 370)
        data[pdf] = {}
        data[pdf]['figures'] = []
        data[pdf]['pages_annotated'] = []
        pdf_flag = 0
        try:
            if not os.path.isdir(xpdf_path+pdf[:-4]):
                std_out = subprocess.check_output([os.environ['Xpdf_PATH'], input_path+'/'+pdf, xpdf_path+pdf[:-4]+'/'])
        except:
            f_log.write(pdf+'\n')
            pdf_flag = 1
        if pdf_flag == 0:
            flag = 0
            wrong_count = 0
            while flag==0 and wrong_count<5:
                try:
                    figures, info = figures_captions_list(input_path, pdf, xpdf_path)
                    flag = 1

                except:
                    wrong_count = wrong_count +1
                    time.sleep(5)
                    info['fig_no_est']=0
                    figures = []

                all_data.append(figures)


    for i in range(1, len(all_data)):
        last_key = list(all_data[i - 1].keys())[-1]
        page_number = int(last_key.split('.')[0][4:]) + 1
        for key, value in list(all_data[i].items()):
            new_key = f"page{page_number}.png"
            all_data[i][new_key] = all_data[i].pop(key)
            page_number += 1

    
    book_data=[]
    for obj in all_data:
        for figure in obj:
            page_no = int(figure[:-4][4:])
            bboxes=obj[figure]
            
            for bbox in bboxes:
                
                if len(bbox[1])>0:
                    data={
                    'page_num':page_no,
                    'figure_bbox':bbox[0],
                    'type':'Figure',
                    'caption_text':bbox[1][1]
                     }
                    book_data.append(data)
                else:
                    data:{
                    'page_num':page_no,
                    'figure_bbox':bbox[0],
                    'type':'Figure',
                    'caption_text':''
                    }
                    book_data.append(data)
    
    figure_extracted=True
    for item in book_data:
        if not 'page_num' in item:
            figure_extracted=False

    if not figure_extracted:
        for item in book_data:
            for bookName, bookData in item.items():
                if 'pages_annotated' in bookData:
                    book_data=[]
    
    return book_data

    