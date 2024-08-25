import sys
sys.path.append('/home/pi/TurboPi/')
import time
import HiwonderSDK.Board as Board
import cv2
from picamera2 import Picamera2
import RPi.GPIO as GPIO
import numpy as np

Board.setPWMServoPulse(5, 1500, 100) #Arm ESC
Board.setPWMServoPulse(1, 1444, 10) #Set Servo to 85
time.sleep(6)

frames=0
count=0
endFrames = 0

turning = False
turnDirection = None
turnBuffer = False

# clockwise = False
# counterclockwise = False

difference = 0
lastdifference = 0

displayLeftArea = 0
displayRightArea = 0
displayOrangeArea = 0
displayTurnCount = 0
displayTurning = 'PD Controller'

font = cv2.FONT_HERSHEY_SIMPLEX

#Camera setup
picam2=Picamera2()
picam2.preview_configuration.main.size = (640,480) #Camera Resolution
picam2.preview_configuration.main.format='RGB888'
picam2.preview_configuration.align()
picam2.preview_configuration.controls.FrameRate=30 #Camera Framerate
picam2.configure("preview")
picam2.start()
if __name__ == '__main__':
    key2_pin = 16
    
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(key2_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
    
    # turn off LED
    Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
    Board.RGB.show()
    
    # turn LED green
    Board.RGB.setPixelColor(0, Board.PixelColor(0, 255, 0))
    Board.RGB.show()
    time.sleep(1)
    
    while GPIO.input(key2_pin) == GPIO.HIGH:
        pass
    
    # turn off LED
    Board.RGB.setPixelColor(0, Board.PixelColor(0, 0, 0))
    Board.RGB.show()
    
    angle = 85.045
    pw_Servo = angle * 11.1 + 500
    Board.setPWMServoPulse(5,1320,100) #Speed
    while True:
        leftarea = 0
        leftcontourindex = 0
        rightarea = 0
        rightcontourindex = 0
        orangearea = 0
        orangecontourindex=0
        
        im = picam2.capture_array()
        
        subim=im[280:325,0:200] #Setting left wall detection area
        subim2=im[280:325,440:640] #Setting right wall detection area
        subim3=im[365:410,180:480]
    
        points = [(0,280), (200,280), (200,325), (0,325)]
        color = (0, 255, 255)
        thickness = 4
        image = cv2.line(im, points[0], points[1], color, thickness)
        image = cv2.line(im, points[1], points[2], color, thickness)
        image = cv2.line(im, points[2], points[3], color, thickness)
        image = cv2.line(im, points[3], points[0], color, thickness)
    
        points = [(440,280), (640,280), (640,325), (440,325)]
        color = (0, 255, 255)
        thickness = 4
        image = cv2.line(im, points[0], points[1], color, thickness)
        image = cv2.line(im, points[1], points[2], color, thickness)
        image = cv2.line(im, points[2], points[3], color, thickness)
        image = cv2.line(im, points[3], points[0], color, thickness)
        
        points = [(150,365), (500,365), (500,410), (150,410)]
        color = (0, 0, 255)
        thickness = 4
        image = cv2.line(im, points[0], points[1], color, thickness)
        image = cv2.line(im, points[1], points[2], color, thickness)
        image = cv2.line(im, points[2], points[3], color, thickness)
        image = cv2.line(im, points[3], points[0], color, thickness)
        
        imgGray = cv2.cvtColor(subim, cv2.COLOR_BGR2GRAY) #Grayscaling for thresholding 
        ret, imgThresh = cv2.threshold(imgGray, 45, 255, cv2.THRESH_BINARY_INV)
        contours, hierarchy = cv2.findContours(imgThresh,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for i in range(len(contours)): #finding largest contour
            cnt = contours[i]
            if cv2.contourArea(cnt) > leftarea:
                leftarea = cv2.contourArea(cnt)
                leftcontourindex = i
        if(leftarea > 0): 
#             print('Left wall: ',leftarea) #Displaying left contour area
            cv2.drawContours(subim, contours, i, (0, 255, 0), 2) #drawing left largest contour
            displayLeftArea = str(int(leftarea))
            cv2.putText(im, displayLeftArea, (7, 250), font, 2, (100, 255, 0), 3, cv2.LINE_AA)
    
        #Right Wall
        imgGray2 = cv2.cvtColor(subim2, cv2.COLOR_BGR2GRAY) #Grayscaling preperation
        ret2, imgThresh2 = cv2.threshold(imgGray2, 45, 255, cv2.THRESH_BINARY_INV)
        contours2, hierarchy2 = cv2.findContours(imgThresh2,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        for i in range(len(contours2)):
            cnt2 = contours2[i]
            if cv2.contourArea(cnt2) > rightarea:
                rightarea = cv2.contourArea(cnt2)
                rightcontourindex = i
        if(rightarea > 0):
#             print('Right Wall: ',rightarea) #displaying right contour area
            cv2.drawContours(subim2, contours2, i, (0, 255, 0), 2) #drawing largest right contour
            displayRightArea = str(int(rightarea))
            cv2.putText(im, displayRightArea, (450, 250), font, 2, (100, 255, 0), 3, cv2.LINE_AA)
#         cv2.imshow("contours2", im)
        
        #Orange Line
        line_hsv = cv2.cvtColor(subim3, cv2.COLOR_BGR2HSV)

        lower_orange = np.array([0, 111, 152]) #Lower threshold for orange colour
        upper_orange = np.array([56, 255, 255]) #Upper threshold for orange colour 
        orange_mask = cv2.inRange(line_hsv, lower_orange, upper_orange) #Orange mask
        
        orangeContours = cv2.findContours(orange_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        
        for i in range(len(orangeContours)): #finding largest orange contour
            cnt3 = orangeContours[i]
            if cv2.contourArea(cnt3) > orangearea:
                orangearea = cv2.contourArea(cnt3)
                orangecontourindex = i
         
        cv2.drawContours(subim3, orangeContours, i, (0, 255, 0), 2) #drawing orange largest contour
        displayOrangeArea = str(int(orangearea))
        cv2.putText(im, displayOrangeArea, (300, 300), font, 2, (100, 255, 0), 3, cv2.LINE_AA)
        
        print("Orange Area:", orangearea)
        
        print("TURN COUNT:", count)
        print("Turning?:", turning)
        print("Turn Direction:", turnDirection)
        print("Turn Buffer:", turnBuffer)
        
        displayTurnCount = str(int(count))
        cv2.putText(im, displayTurnCount, (560, 60), font, 2, (100, 255, 0), 3, cv2.LINE_AA) 
        cv2.putText(im, displayTurning, (7, 60), font, 2, (100, 255, 0), 3, cv2.LINE_AA) 
        
        if orangearea > 700:
            frames += 1
            if frames>40:
                count+=1
                frames=0
#             if clockwise == True:
#                 if frames>30:
#                     count+=1
#                     frames=0
#             elif counterclockwise == True:
#                 if frames>40:
#                     count+=1
#                     frames=0
        
        if not turning: 
            if leftarea < 150: #Sharp turn left
                turning = True
                turnDirection = 'left'
                print("TURNING LEFT")
#                 counterclockwise = True
#                 clockwise = False
                        
            elif rightarea < 150: #Sharp turn right
                turning = True
                turnDirection = 'right'
                print("TURNING RIGHT")
#                 counterclockwise = False
#                 clockwise = True

        if turnDirection == 'left' and turning == True:
            Board.setPWMServoPulse(1,1832, 1)
            frames += 1
            print("frames:",frames)
            displayTurning = 'Turning Left'
            if frames < 7:
                turnBuffer = True
            elif frames > 7:
                turnBuffer = False
#             if frames>25:
#                 count+=1
#                 frames=0
                
        elif turnDirection == 'right' and turning == True:
            Board.setPWMServoPulse(1,955, 1)
            frames += 1
            print("frames:",frames)
            displayTurning = 'Turning Right'
            if frames < 7:
                turnBuffer = True
            elif frames > 7:
                turnBuffer = False
#             if frames>25:
#                 count+=1
#                 frames=0
        
        if turning == True and leftarea > 250 and rightarea > 250:
            turning = False
            turnDirection = None
            lastdifference = 0
            
        if not turning and turnDirection == None and turnBuffer == False:
            #PD CONTROLLER 
            turnBuffer = False
            print("PD ACTIVATED")
            displayTurning = 'PD Controller'
            difference = rightarea - leftarea
            correction = 0.01 * difference + 0.001 * (difference - lastdifference)
            angle = 85.045 + correction
            
            if angle > 120:
                angle = 120
            elif angle < 40:
                angle = 40
            
            pw = int(11.1 * angle + 500)
            Board.setPWMServoPulse(1, pw, 1)
            lastdifference = difference
    
        if count>=12: #all turns have been completed
            endFrames+=1
            
            if endFrames > 85: #counting frames to ensure robot ends in correct place
                Board.setPWMServoPulse(5,1500,100) #Stopping the motor
                Board.setPWMServoPulse(1,1500,100) #Straightening wheels
                break #exiting loop 
        
        if len(sys.argv) > 1 and sys.argv[1] == 'Debug': #Debug mode
            cv2.imshow('contours2', im)
        
            if cv2.waitKey(1)==ord('q'):
                Board.setPWMServoPulse(5,1500,100)
                Board.setPWMServoPulse(1,1444,100)
                cv2.destroyAllWindows()
                break
        
cv2.destroyAllWindows()