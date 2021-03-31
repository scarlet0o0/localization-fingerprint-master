import serial

s = serial.Serial('COM10', 9600, timeout=2)
if not s.isOpen():
    s.open()

while True:
    line = str(s.readline())
    line = line[2:6]
    print(line)
# three FIRE in row -- send fire alarm

s.close()