from machine import Pin, PWM, I2C
from time import sleep_ms

# Setup I2C OLED
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled_addr = 0x3C

# Setup Servo di GPIO15
servo = PWM(Pin(15), freq=50)

# Setup LED di GPIO2
led = Pin(2, Pin.OUT)

# Setup Tombol di GPIO4
button = Pin(4, Pin.IN, Pin.PULL_UP)  # PULL_UP artinya aktif saat LOW

# Setup Buzzer di GPIO5
buzzer = Pin(5, Pin.OUT)

# Font huruf besar minimal
font = {
    'P': [0x7F, 0x09, 0x09, 0x09, 0x06],
    'I': [0x00, 0x41, 0x7F, 0x41, 0x00],
    'N': [0x7F, 0x10, 0x08, 0x04, 0x7F],
    'T': [0x01, 0x01, 0x7F, 0x01, 0x01],
    'U': [0x3F, 0x40, 0x40, 0x40, 0x3F],
    'R': [0x7F, 0x09, 0x19, 0x29, 0x46],
    'B': [0x7F, 0x49, 0x49, 0x49, 0x36],
    'E': [0x7F, 0x49, 0x49, 0x49, 0x41],
    'K': [0x7F, 0x08, 0x14, 0x22, 0x41],
    'A': [0x7E, 0x09, 0x09, 0x09, 0x7E],
    'O': [0x3E, 0x41, 0x41, 0x41, 0x3E],
    'C': [0x3E, 0x41, 0x41, 0x41, 0x22],
    ' ': [0x00, 0x00, 0x00, 0x00, 0x00],
}

def oled_cmd(cmd):
    i2c.writeto(oled_addr, b'\x00' + bytes([cmd]))

def oled_init():
    for cmd in [0xAE, 0xA8, 0x3F, 0xD3, 0x00, 0x40, 0xA1, 0xC8,
                0xDA, 0x12, 0x81, 0x7F, 0xA4, 0xA6, 0xD5, 0x80,
                0x8D, 0x14, 0xAF]:
        oled_cmd(cmd)

def oled_clear():
    for i in range(8):
        oled_cmd(0xB0 + i)
        oled_cmd(0x00)
        oled_cmd(0x10)
        i2c.writeto(oled_addr, b'\x40' + bytes([0x00]*128))

def oled_write_text(text, page=0):
    oled_cmd(0xB0 + page)
    oled_cmd(0x00)
    oled_cmd(0x10)
    for char in text.upper():
        data = font.get(char, font[' '])
        i2c.writeto(oled_addr, b'\x40' + bytes(data + [0x00]))

def set_angle(angle):
    min_duty = 1638
    max_duty = 8192
    duty = int(min_duty + (angle / 180) * (max_duty - min_duty))
    servo.duty_u16(duty)

def blink_led():
    led.on()
    sleep_ms(100)
    led.off()

def buzz(duration=200):
    buzzer.on()
    sleep_ms(duration)
    buzzer.off()

# Inisialisasi OLED
oled_init()
oled_clear()

# Status pintu, awalnya tertutup
pintu_terbuka = False

while True:
    if button.value() == 0:  # Tombol ditekan (karena pakai PULL_UP)
        sleep_ms(200)  # Debounce delay
        if not pintu_terbuka:
            # Buka pintu
            set_angle(90)
            oled_clear()
            oled_write_text("PINTU", page=1)
            oled_write_text("TERBUKA", page=3)
            blink_led()
            buzz()
            pintu_terbuka = True
        else:
            # Tutup pintu
            set_angle(0)
            oled_clear()
            oled_write_text("PINTU", page=1)
            oled_write_text("TERTUTUP", page=3)
            blink_led()
            buzz()
            pintu_terbuka = False
        # Tunggu sampai tombol dilepas
        while button.value() == 0:
            sleep_ms(10)