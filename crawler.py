# -*- coding: utf-8 -*-
"""
Created on Mon Oct 16 20:32:27 2017
@author: 望
"""
import requests
import re
import os
from pypinyin import pinyin, lazy_pinyin


import tensorflow as tf
import detect_face
import cv2
global sess, pnet, rnet, onet
with tf.Graph().as_default():
    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.6)
    sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
    with sess.as_default():
        pnet, rnet, onet = detect_face.create_mtcnn(sess, '../facenet/src/align')

def onlyone_face(imgfile):
    
    minsize = 60  # minimum size of face
    threshold = [0.6, 0.7, 0.7]  # three steps's threshold
    factor = 0.709  # scale factor
    margin = 44
    frame_interval = 3
    batch_size = 1000
    image_size = 182
    input_image_size = 160
    global sess, pnet, rnet, onet
    with sess.as_default():      
        frame = cv2.imread(imgfile)
        bounding_boxes, _ = detect_face.detect_face(frame, minsize, pnet, rnet, onet, threshold, factor)
        nrof_faces = bounding_boxes.shape[0]
        return nrof_faces==1


def getHTMLText(url):
	try:
		r = requests.get(url,timeout=30)
		r.raise_for_status()
		r.encoding = r.apparent_encoding
		return r.text
	except Exception as e:
		print(e)
 
def getPageUrls(text,name):
    re_pageUrl=r'href="(.+)">\s*<img src="(.+)" alt="'+name
    return re.findall(re_pageUrl,text)
  
def downPictures(text,root,name, cnt):
    pageUrls=getPageUrls(text,name)  
    titles=re.findall(r'alt="'+name+r'(.+)" ',text)
    
    for i in range(len(pageUrls)):
        pageUrl=pageUrls[i][0]
        #path = root + titles[i]+ "//"
        path = root+"/"
        if not os.path.exists(path):
            os.mkdir(path)
        if not os.listdir(path) or os.listdir(path):             
            pageText=getHTMLText(pageUrl)
            totalPics=int(re.findall(r'<em>(.+)</em>）',pageText)[0])
            downUrl=re.findall(r'href="(.+?)" class="">下载图片',pageText)[0]
            
            while(cnt<=totalPics and cnt<=30):
                picPath=path+str(cnt)+".jpg"
                r=requests.get(downUrl)
                with open(picPath,'wb') as f:
                    f.write(r.content)
                    f.close()
                
                #     
                print('{} - 第{}张下载已完成\n'.format(titles[i],cnt))
                # 检查人脸数量，只保留1个人脸的照片
                if onlyone_face(picPath):
                    
                    cnt+=1     
                else:
                    # 删掉不合格的文件
                    
                    os.remove(picPath)
                    print('{} - 第{}张文件不合格，已删除\n'.format(titles[i],cnt))             
                nextPageUrl=re.findall(r'href="(.+?)">下一张',pageText)[0]
                pageText=getHTMLText(nextPageUrl)
                downUrl=re.findall(r'href="(.+?)" class="">下载图片',pageText)[0]
    return cnt
 
def main(name=None):  
    if not name:
        name=input("请输入你喜欢的明星的名字:")
    nameUrl="http://www.win4000.com/mt/"+''.join(lazy_pinyin(name))+".html"        
    print(nameUrl)
    try:
        text=getHTMLText(nameUrl)
        cnt=0
        if not re.findall(r'暂无(.+)!',text):       
            root = "in_faces/"+''.join(lazy_pinyin(name))+"/"
            if not os.path.exists(root):
                os.mkdir(root)
            cnt = downPictures(text,root,name, cnt)
            try:
                nextPage=re.findall(r'next" href="(.+)"',text)[0]
                while(nextPage):
                    nextText=getHTMLText(nextPage)
                    cnt = downPictures(nextText,root,name, cnt)              
                    nextPage=re.findall(r'next" href="(.+)"',nextText)[0]
            except IndexError:
                print("已全部下载完毕")
    except Exception as e:
        print("不好意思，没有{}的照片".format(name), e)
        #print(e)
        import traceback
        traceback.print_exc()
    return
 
if __name__ == '__main__':
    import sys
    if len(sys.argv)>1:
        for arg in sys.argv[1:]:
            main(arg)
    else:
        main()
# --------------------- 
# 作者：ACLJW 
# 来源：CSDN 
# 原文：https://blog.csdn.net/qq_37754288/article/details/78255730 
# 版权声明：本文为博主原创文章，转载请附上博文链接！

