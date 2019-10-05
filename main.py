from flask import Flask, escape, request, render_template
import json
import RPi.GPIO as GPIO
import time



def getFileText(fileName):
    fileCont = open(fileName, 'r')
    fileText = fileCont.read()
    fileCont.close()
    return fileText
    
def writeFile(fileName, value):
    fileCont = open(fileName, 'w')
    fileCont.write(value)
    fileCont.close()






#monitor when the system is in action
writeFile("wateringAction", "false")
#wateringAction = False

#pin assignments
servoPin = 17
pumpPin = 25
directionPin = 23
stepPin = 18
stepperEnable = 24

#state definition
LOW = False
HIGH = True
stepSpeed = 0.01
#swings = 36 #the number of times the sector will be covered
swings = 3 #the number of times the sector will be covered
pumpRange = 5 #the angle the servo will turn per swing

#pin initialization
GPIO.setmode(GPIO.BCM)
GPIO.setup(pumpPin, GPIO.OUT)
GPIO.setup(directionPin, GPIO.OUT)
GPIO.setup(stepPin, GPIO.OUT)
GPIO.setup(stepperEnable, GPIO.OUT)
GPIO.setup(servoPin, GPIO.OUT)

#pwm = GPIO.PWM(pwmPin, 50)  # Initialize PWM on pwmPin 100Hz frequency
servoAngle = GPIO.PWM(servoPin, 50)
#GPIO.setup(butPin, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Button pin set as input w/ pull-up

#servoAngle.ChangeDutyCycle(7.5) = Neutral at 50HZ the 1.5ms 
#servoAngle.ChangeDutyCycle(12.5) = 180 at 50HZ the 2.5ms
#servoAngle.ChangeDutyCycle(2.5) = 0 at 50HZ the 0.5ms
#servoAngle.stop()

servoAngle.stop() # stop PWM
GPIO.cleanup() # cleanup all GPIO

def reInit():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pumpPin, GPIO.OUT)
    GPIO.setup(directionPin, GPIO.OUT)
    GPIO.setup(stepPin, GPIO.OUT)
    GPIO.setup(stepperEnable, GPIO.OUT)
    GPIO.setup(servoPin, GPIO.OUT)


#digital output
def digitalWrite(pinNumber, state):
    if state == LOW or state == 'LOW' or state == 0:
        GPIO.output(pinNumber, GPIO.LOW)
    elif state == HIGH or state == 'HIGH' or state == 1:
        GPIO.output(pinNumber, GPIO.HIGH)

def digitalRead(pinNumber):
    return GPIO.input(pinNumber)
    
    
def clockWise():
    digitalWrite(stepperEnable, 0)
    time.sleep(stepSpeed)
    digitalWrite(directionPin, 0)
    time.sleep(stepSpeed)
    digitalWrite(stepPin, 1)
    time.sleep(stepSpeed)
    digitalWrite(stepPin, 0)
    time.sleep(stepSpeed)
    digitalWrite(stepperEnable, 1)

   
def antiClockWise():
    digitalWrite(stepperEnable, 0)
    time.sleep(stepSpeed)
    digitalWrite(directionPin, 1)
    time.sleep(stepSpeed)
    digitalWrite(stepPin, 1)
    time.sleep(stepSpeed)
    digitalWrite(stepPin, 0)
    time.sleep(stepSpeed)
    digitalWrite(stepperEnable, 1)


def pumpActivate():
    digitalWrite(pumpPin, LOW)

def pumpStop():
    digitalWrite(pumpPin, HIGH)

def initFnc():
    reInit()
    digitalWrite(stepperEnable, 1)  #disable the stepper motor
    pumpStop()
    servoAngle.start(7.5)

app = Flask(__name__)



#code start
initFnc()





@app.route('/')
def index():
    #sensors = request.args.get("sensors")
    sensors = request.args.get("sensors")
    if sensors:
        writeFile("sectors", sensors)
        
    sectors = getFileText('sectors')
    sectors = int(sectors)
    sectorAngle = 360/sectors
    skew = 0
    if sectorAngle == 90:
        skew = 0
    elif sectorAngle < 90:
        skew = 90 - sectorAngle
    elif sectorAngle > 90:
        skew = 180 - sectorAngle + 90
    elif sectorAngle == 180:
        skew = 91
        
    print("skew: ", skew)
    print("sectors: ", sectors)
    print("sectorAngle: ", sectorAngle)
    print(json.dumps(sensors))
    
    index7 = '<div class="wrapper mt-4">'
    if sectorAngle == 180:
        index7 = '<div style="background-color: #ccc;" class="wrapper mt-4">'
    for i in range(sectors):
        index7 += '<div class="sector circlic-area" style="transform: rotate(' + str(i*sectorAngle) + 'deg) skew(' + str(skew) + 'deg);"></div>'
    index7 += '</div>'
    
    
    #page = getFileText('template/index.html')
    page = getFileText('template/index1.html')
    page += getFileText('template/index2.html')
    page += getFileText('template/index3.html')
    page += getFileText('template/index4.html')
    page += getFileText('template/index5.html')
    page += getFileText('template/index6.html')
    page += index7
    page += getFileText('template/index8.html')

    return page



@app.route('/direction')
def direction():
    direction = request.args.get("direction")
    print(direction)
    
    if direction == "Anti-Clock-Wise":
        print("\t Executed Anti-Clock-Wise")
        for x in range(10):
            antiClockWise()
    elif direction == "Clock-Wise":
        print("\t Executed Clock-Wise")
        for x in range(10):
            clockWise()
    
    #page = getFileText('template/index.html')
    return index()
    
#wateringAction = False    
@app.route('/drysector')
def drysector():
    #if the machie is prayig d not respond to new call
    wateringAction = getFileText('wateringAction')
    if wateringAction == "true":
        return
    
    #the machine has started a new call
    writeFile("wateringAction", "true")
    #wateringAction = True
    
    
    startAngle = request.args.get("startangle")
    

    sectors = getFileText('sectors')
    sectors = int(sectors)
    sectorAngle = 360/sectors
    startAngle = int(startAngle)

    print("-----------------------------------------------")
    print("---startAngle: "+ str(startAngle))
    print("---sectorAngle: "+ str(sectorAngle))
    print("-----------------------------------------------")

    initialStep = int(400*startAngle/360)
    angleStep = int(400*sectorAngle/360)     #within the sector

    #taking the pump to the needed sector
    for s in range(initialStep):
        clockWise()
    
    pumpActivate()      #start spraying water
    dutyStep = (12.5-2.5)/5
    base = 2.5
    servoAngle.ChangeDutyCycle(base)

    #water spraying action
    for swing in range(swings):
        base += dutyStep
        for angleWithSector in range(angleStep):
            clockWise()
        for angleWithSector in range(angleStep):
            antiClockWise()
        servoAngle.ChangeDutyCycle(base)

    #returning the pump to the initial state
    for s in range(initialStep):
        antiClockWise()


    pumpStop()
    
            
    #the machine ending call
    writeFile("wateringAction", "false")
    #wateringAction = False



    return



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)

