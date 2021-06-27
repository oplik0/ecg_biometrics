# A micropython program for basic ecg biometrics on Kendryte K210
from machine import I2C
from Maix import GPIO, KPU, FFT
from fpioa_manager import fm
from ads1x15 import ADS1115
from utime import sleep_ms
from cmath import sqrt

fm.register(35, fm.fpioa.I2C1_SCLK)
fm.register(34, fm.fpioa.I2C1_SDA)
i2c = I2C(I2C.I2C1, scl=35, sda=34)
adc = ADS1115(i2c, 72, 4)

fm.register(0, fm.fpioa.GPIO0)
fm.register(1, fm.fpioa.GPIO1)
LO1, LO2 = GPIO(GPIO.GPIO0, GPIO.IN), GPIO(GPIO.GPIO1, GPIO.IN)

command = "NONE"
registered = {}
model = KPU.load("/sd/heart.kmodel")



def get_signal():
    buff = []
    adc.set_conv(4, 1)
    while len(buff) < 128*45:
        buff.add(adc.read_rev())
    return buff
def process_signal(signal):
    norm = sqrt(sum(map(lambda x: x**2, signal)))
    normalised = list(map(lambda x: (complex(x/norm).real * 256) % 256, signal))
    result = list(FFT.run(bytearray(l), 512))
    return result

def classify(signal):
    return KPU.forward(model, signal)

def find_match(result):
    for user, value in registered.items():
        distance = sum([abs(abs(x)-abs(y)) for x, y in zip(result, value)])
        if distance<0.15:
            return user
    return False

while(True):
    command=input("input a command (available commands: READ and REGISTER): ").upper()
    if command=="READ" or command=="REGISTER":
        if not LO1.value() and not LO2.value():
            signal = get_signal()
            processed = process_signal(signal)
            classes = classify(signal)
            if command == "READ":
                user = find_match(classes)
                if user:
                    print("Potwierdzono tożsamość użytkownika", user)
                else:
                    print("Nie udało się zweryfikować tożsamości")
            elif command=="REGISTER":
                user = input("Wprowadź nazwę dla użytkownika: ")
                registered[user] = classes
            command = ""
