import curses
import epd4in2b
#should these be imported from PIL (python image library? adafruit uses this)
import Image
import ImageFont
import ImageDraw
import time
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#Pins on RPi
clockPin = 13
latchPin = 16
dataPinOut = 12
dataPinIn = 27
resetPin = 06


#Setting up GPIOs
GPIO.setup(clockPin, GPIO.OUT)
GPIO.setup(latchPin, GPIO.OUT)
GPIO.setup(dataPinOut, GPIO.OUT)
GPIO.setup(dataPinIn, GPIO.IN)
GPIO.setup(resetPin, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

#ShiftOut lists. The first 595 is actually the last 8
offList =[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
resetList = [0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,1]
redList = [0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0]
yellowRedList = [0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0]
yellowYellowList = [0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0]
greenYellowList = [0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0]
greenList = [0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0]
judgeList = [0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0]
launch1List = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0]
launch2List = [0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0]
onList = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0]
lastList = [0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0]

#This resets the Pi and sends a HIGH to the Arduino reset pin. LEDs should be red
def reset(dataPinOut, dataPinIn, clockPin, latchPin,newOutput):
    
    shiftOut(dataPinOut, clockPin, latchPin,newOutput)
    print("resetting")
    time.sleep(3)

#EPD is sent the number of lines and text
def epd(lines,string1,string2=""):
    #Setup
    epd = epd4in2b.EPD()
    epd.init()
    font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', 36)
    
    #refresh
    image_red = Image.new('1', (epd4in2b.EPD_WIDTH, epd4in2b.EPD_HEIGHT), 255)    # 255: clear the frame
    draw_red = ImageDraw.Draw(image_red)
    image_black = Image.new('1', (epd4in2b.EPD_WIDTH, epd4in2b.EPD_HEIGHT), 255)    # 255: clear the frame
    draw_black = ImageDraw.Draw(image_black)
    
    #display
    if lines == 1:
        draw_red.text((20, 10), string1, font = font, fill = 0)
        epd.display_frame(epd.get_frame_buffer(image_black), epd.get_frame_buffer(image_red))
    
    elif lines == 2:
        draw_red.text((45, 20), string1, font = font, fill = 0)
        draw_red.text((65, 70), string2, font = font, fill = 0)
        epd.display_frame(epd.get_frame_buffer(image_black), epd.get_frame_buffer(image_red))
    
    else:
        print("Invalid number of lines")

#This reads the shift register and shifts the bits into inValue. I needed to output LEDS or they would turn off.
def readPins(dataPinOut, dataPinIn, clockPin, latchPin,currentOutput):
    GPIO.output(clockPin,0)
    i = 0
    inValue = 0
    for i in range(0,16):
        inValue |= ((GPIO.input(dataPinIn)) << (15-i)) #When I used a list, the bits would be high for no reason
        GPIO.output(dataPinOut,currentOutput[i]) #Lists work fine for output, but I think the order is now messed up.
        time.sleep(.003) #idk if this pause is needed
        GPIO.output(clockPin,1) #toggling the clock to move fwd
        time.sleep(.003)
        GPIO.output(clockPin,0)
        i += 1
    GPIO.output(latchPin,0) #latch the 16 bits for in and out
    time.sleep(.003)
    GPIO.output(latchPin,1)

#I needed to format the bit shifted input to show all the zeros. This turns it into a list and from int to a string
    binary = format(inValue, '016b')
    #delete this sleep!! and print
    print(binary)
    time.sleep(1)
    return binary

#this is for when the judge button is pressed
def judgePin(pointsPossible, dataPinOut, dataPinIn, clockPin, latchPin,judgeOutput):
    GPIO.output(clockPin,0)
    j = 0
    #turing all LEDS on
    for j in range(0,16):
        GPIO.output(dataPinOut,judgeOutput[j])
        GPIO.output(clockPin,1)
        GPIO.output(clockPin,0)
        j += 1
    GPIO.output(latchPin,0) #toogle latch
    GPIO.output(latchPin,1)
    epd(1,"Judge Pressed")
    time.sleep(5) #so you know you pushed it. Think of this also as a penalty

    GPIO.output(clockPin,0)
    i = 0
    inValue = 0
    for i in range(0,16):
        inValue |= ((GPIO.input(dataPinIn)) << (15-i)) #When I used a list, the bits would be high for no reason
        time.sleep(.003) #idk if this pause is needed
        GPIO.output(clockPin,1) #toggling the clock to move fwd
        time.sleep(.003)
        GPIO.output(clockPin,0)
        i += 1
    GPIO.output(latchPin,0) #latch the 16 bits for in and out
    time.sleep(.003)
    GPIO.output(latchPin,1)

#changing outputs without reading shiftIn
def shiftOut(dataPinOut, clockPin, latchPin,newOutput):
    GPIO.output(clockPin,0)
    j = 0
    for j in range(0,16):
        GPIO.output(dataPinOut,newOutput[j])
        GPIO.output(clockPin,1)
        GPIO.output(clockPin,0)
        j += 1
    GPIO.output(latchPin,0)
    GPIO.output(latchPin,1)

#looking for one pin being high
#Points, Shift Register Settings, Pin to check, High/Low, 3 Output Arrays, EPD stuff
def landerOne(pointsPossible, dataPinOut, dataPinIn, clockPin, latchPin,checkStatus,highLow,currentOutput, newOutput,judgeOutput, lines,string1,string2=""):
    
    epd(lines,string1,string2) #Send text to EPD
    while 1:
        binary = readPins(dataPinOut, dataPinIn, clockPin, latchPin,currentOutput) #keeps polling using the readPin func
        
        
        if binary[checkStatus] == highLow: #changing to binary format makes it string in a list
            shiftOut(dataPinOut, clockPin, latchPin,newOutput)
            points = pointsPossible #The possible points are awarded for completing task
            break
        
        elif binary[1] == "1": #Judge pushes button to move on
            judgePin(pointsPossible,dataPinOut, dataPinIn, clockPin, latchPin,judgeOutput)
            points = 0 #no points are awarded
            break
 
        elif GPIO.input(resetPin) == 1:
            print("RESET")
            points =0
            break

    return points #sends points out 0 or awarded

#Needed a new function for this since it flashes LEDs
def evac(dataPinOut, clockPin, latchPin,newOutput,judgeOutput,lastList, lines,string1,string2=""):

    epd(lines,string1,string2) #Send text to EPD

    for k in range (0,10): #Flash on and off for 10 cycles
            GPIO.output(clockPin,0)
            m = 0
            for m in range(0,16):
                GPIO.output(dataPinOut,newOutput[m])
                GPIO.output(clockPin,1)
                GPIO.output(clockPin,0)
                m += 1
            GPIO.output(latchPin,0)
            GPIO.output(latchPin,1)
            
            time.sleep(1)
            GPIO.output(clockPin,0)
            n = 0
            for n in range(0,16):
                GPIO.output(dataPinOut,judgeOutput[n])
                GPIO.output(clockPin,1)
                GPIO.output(clockPin,0)
                n += 1
            GPIO.output(latchPin,0)
            GPIO.output(latchPin,1)
            time.sleep(1)
            k+=1

    q = 0 #Turn off LEDs and siren
    for q in range(0,16):
        GPIO.output(dataPinOut,lastList[q])
        GPIO.output(clockPin,1)
        GPIO.output(clockPin,0)
    n += q
    GPIO.output(latchPin,0)
    GPIO.output(latchPin,1)
    time.sleep(1)


#Needed a separate function for keyboard input
def password(pointsPossible,dataPinOut, dataPinIn, clockPin,latchPin,currentOutput,judgeOutput,lines,string1,string2=""):
    epd(lines,string1,string2) #Send text to EPD
    screen = curses.initscr()
    curses.noecho()
    curses.halfdelay(3)
    screen.keypad(True)
    resetPressed = 0
    judgePressed = 0
    
    #This lets it put the letters in order and also allows for use of judge and reset button
    while 1:
        while 1:
            binary = readPins(dataPinOut, dataPinIn, clockPin, latchPin,currentOutput)
            char = screen.getch()
            if char == ord('M') or char == ord('m'):
                epd(1,"m","")
                break
            
            elif binary[1] == "1":
                judgePressed = 1
                break
            
            elif GPIO.input(resetPin) == 1:
                resetPressed = 1
                break
        if resetPressed == 1:
            points = 0
            break
        elif judgePressed == 1:
            points = 0
            judgePin(pointsPossible, dataPinOut, dataPinIn, clockPin, latchPin,judgeOutput)
            break

        while 1:
            binary = readPins(dataPinOut, dataPinIn, clockPin, latchPin,currentOutput)
            char = screen.getch()
            if char == ord('a')or char == ord('A'):
                print("ma")
                epd(1,"ma","")
                break
        
            elif binary[1] == "1":
                judgePressed = 1
                break

            elif GPIO.input(resetPin) == 1:
                resetPressed = 1
                break
        if resetPressed == 1:
            points = 0
            break
        elif judgePressed == 1:
            points = 0
            judgePin(pointsPossible, dataPinOut, dataPinIn, clockPin, latchPin,judgeOutput)
            break

        while 1:
            binary = readPins(dataPinOut, dataPinIn, clockPin, latchPin,currentOutput)
            char = screen.getch()
            if char == ord('r') or char == ord('R'):
                epd(1,"mar","")
                break
            
            elif binary[1] == "1":
                judgePressed = 1
                break
            
            elif GPIO.input(resetPin) == 1:
                resetPressed = 1
                break
        if resetPressed == 1:
            points = 0
            break
        elif judgePressed == 1:
            points = 0
            judgePin(pointsPossible, dataPinOut, dataPinIn, clockPin, latchPin,judgeOutput)
            break

        while 1:
            binary = readPins(dataPinOut, dataPinIn, clockPin, latchPin,currentOutput)
            char = screen.getch()
            if char == ord('s') or char == ord('S'):
                epd(1,"mars","")
                break
            
            elif binary[1] == "1":
                judgePressed = 1
                break

            elif GPIO.input(resetPin) == 1:
                resetPressed = 1
                break

        if resetPressed == 1:
            points = 0
            break
        elif judgePressed == 1:
            points = 0
            judgePin(pointsPossible, dataPinOut, dataPinIn, clockPin, latchPin,judgeOutput)
            break
        else:
            points = pointsPossible
            break
    return points

try:
    #landerOne(pointsPossible, dataPinOut, dataPinIn, clockPin, latchPin,checkStatus,currentOutput, newOutput,judgeOutput, lines,string1,string2=""):
    while 1:
        switchDict = {"card":0,"judge":1,"signal":2,"telemetry":3,"oxygen":4,"methane":5,"turbo":6,"lock":7,"ignition":8,"alarm":9,"launch":10}
        pointsDict = {"insertCardPoints":10,"enableTelemetryPoints":5,"signalLockPoints":10,"enterPasswordPoints":10,"prepareEnginePoints":5,"prepareCapsulePoints":5,"closeLatchPoints":5,"launchPoints":5}
        while 1:
            print("starting")
            reset(dataPinOut, dataPinIn, clockPin, latchPin,resetList)
            insertCard = landerOne(pointsDict["insertCardPoints"],dataPinOut, dataPinIn, clockPin, latchPin,switchDict["card"],"1",redList,redList,judgeList,2,"LAUNCH CONTROL","NOT INSERTED")
            if GPIO.input(resetPin) == 1:
                print("RESET")
                break
            
            enableTelemetry = landerOne(pointsDict["enableTelemetryPoints"],dataPinOut, dataPinIn, clockPin, latchPin,switchDict["telemetry"],"1",yellowRedList,yellowYellowList,judgeList,1,"ENABLE TELEMETRY")
            if GPIO.input(resetPin) == 1:
                print("RESET")
                break

            signalLock = landerOne(pointsDict["signalLockPoints"],dataPinOut, dataPinIn, clockPin, latchPin,switchDict["signal"],"1",yellowYellowList,yellowYellowList,judgeList,2,"AUTO ALIGN FAIL","MANUALLY ALIGN")
            if GPIO.input(resetPin) == 1:
                print("RESET")
                break
            
            passwordTotal = password(pointsDict["enterPasswordPoints"],dataPinOut, dataPinIn, clockPin, latchPin,yellowYellowList,judgeList,1,"ENTER PASSWORD")
            if GPIO.input(resetPin) == 1:
                print("RESET")
                break
            
            prepareEngine = landerOne(pointsDict["prepareEnginePoints"],dataPinOut, dataPinIn, clockPin,latchPin,switchDict["methane"],"1",yellowYellowList,greenYellowList,judgeList,1,"PREPARE ENGINE")
            if GPIO.input(resetPin) == 1:
                print("RESET")
                break

            prepareCapsule = landerOne(pointsDict["prepareCapsulePoints"],dataPinOut, dataPinIn, clockPin,latchPin,switchDict["lock"],"1",greenYellowList,greenList,judgeList,1,"PREPARE CAPSULE")
            if GPIO.input(resetPin) == 1:
                print("RESET")
                break

            closeLatch = landerOne(pointsDict["closeLatchPoints"],dataPinOut, dataPinIn, clockPin, latchPin,switchDict["judge"],"1",greenList,greenList,judgeList,1,"CLOSE ACCESS DOOR")

            launchButton = landerOne(pointsDict["launchPoints"],dataPinOut, dataPinIn, clockPin, latchPin,switchDict["launch"],"0",greenList,offList,judgeList,1,"PRESS LAUNCH")
            if GPIO.input(resetPin) == 1:
                print("RESET")
                break
            
            countDown = evac(dataPinOut,clockPin,latchPin,launch1List,launch2List,lastList,2,"EVACUATE THE","BLAST AREA!")

            pointsTotal = insertCard + enableTelemetry + signalLock + prepareEngine + prepareCapsule + closeLatch + passwordTotal + launchButton
            total = str(pointsTotal)

            epd(2,"Possible Points Earned",total)
            while 1:
                if GPIO.input(resetPin) == 1:
                    print("RESET")
                    break

except KeyboardInterrupt: #CTRL+C
    GPIO.cleanup()
