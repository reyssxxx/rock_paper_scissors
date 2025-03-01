import mediapipe
import cv2
from collections import Counter
import random
from time import sleep
import time


#Используем MediaPipe для считывания позиции рук в реальном времени
drawingModule = mediapipe.solutions.drawing_utils
handsModule = mediapipe.solutions.hands

my_list=['rock','scissors', 'paper' ]

h=480
w=640
tip=[8,12,16,20]
mid=[6,10,14,18] 
fingers=[]
finger=[]


               

counter=0

def brawl(frame1):     
        with handsModule.Hands(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=1) as hands:
                                           
            list=[] 
            results = hands.process(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))
            
            #Incase the system sees multiple hands this if statment deals with that and produces another hand overlay
            if results.multi_hand_landmarks != None:
                for handLandmarks in results.multi_hand_landmarks:
                    drawingModule.draw_landmarks(frame1, handLandmarks, handsModule.HAND_CONNECTIONS)
                    list=[]
                    for id, pt in enumerate (handLandmarks.landmark):
                        x = int(pt.x * w)
                        y = int(pt.y * h)
                        list.append([id,x,y])  #Gets landmarks position
                    
            #print('list=', list)
            a = list
            b= findnameoflandmark(frame1, hands)

               
            if len(b and a)!=0:  #a[id,x,y]; x,y=[0,0] on top left of the screen; and x,y=[1,1] at the bottom right
                fingers=[]
                for id in range(0,4):
                    if tip[id]==8 and mid[id]==6:  #index_finger_tip landmark 
                        if (a[tip[id]][2:] < a[mid[id]][2:]):
                            fingers.append(1)
                        else:
                            fingers.append(0)
                    if tip[id]==12 and mid[id]==10: #middle_finger_tip landmark
                        if (a[tip[id]][2:] < a[mid[id]][2:]):
                            fingers.append(1)
                        else:
                            fingers.append(0)
                    if tip[id]==16 and mid[id]==14: #ring_finger_tip landmark
                        if (a[tip[id]][2:] < a[mid[id]][2:]):
                            fingers.append(1)
                        else:
                            fingers.append(0)
                    if tip[id]==20 and mid[id]==18: #pinky_finger_tip landmark
                        if (a[tip[id]][2:] < a[mid[id]][2:]):
                            fingers.append(1)
                        else:
                            fingers.append(0)
                                                                           
                x=fingers                 
                        #rock
                if x[0] == 0 and x[1]==0 and x[2]==0 and x[3]==0:  #rock vs rock
                            return 'Камень'
                        #scissors
                if x[0] == 1 and x[1]==1 and x[2]==0 and x[3]==0:  #scissors vs rock
                            return 'Ножницы'                   
                        #paper
                if x[0] == 1 and x[1]==1 and x[2]==1 and x[3]==1:  #paper vs rock
                            return 'Бумага'
                return None                        
                            
def findnameoflandmark(frame1, hands):
     list=[]
     results = hands.process(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))
     if results.multi_hand_landmarks != None:
        for handLandmarks in results.multi_hand_landmarks:


            for point in handsModule.HandLandmark:
                 list.append(str(point).replace ("< ","").replace("HandLandmark.", "").replace("_"," ").replace("[]",""))
     return list