import serial

s = serial.Serial('COM10', 9600, timeout=2)
if not s.isOpen():
    s.open()
num=0
f="n"
while True:
    line = str(s.readline())
    line = line[2:6]
    if(line=="\'"):
        num=num+1
    elif(line=="FIRE"):
        f="FIRE"
        num=0
    if(num>=3):
        f="n"
        num=0
    print(f)

# three FIRE in row -- send fire alarm

s.close()