import time
import qwiic_button
import sys
import vlc

import board
from adafruit_seesaw import seesaw, rotaryio, digitalio

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
seesaw = seesaw.Seesaw(i2c, addr=0x36)

seesaw_product = (seesaw.get_version() >> 16) & 0xFFFF
print("Found product {}".format(seesaw_product))
if seesaw_product != 4991:
    print("Wrong firmware loaded?  Expected 4991")

# Configure seesaw pin used to read knob button presses
# The internal pull up is enabled to prevent floating input
seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
button = digitalio.DigitalIO(seesaw, 24)


def run_example():

    my_button = qwiic_button.QwiicButton()
    instance = vlc.Instance('--aout=alsa')
    p = instance.media_player_new()
    m = instance.media_new('drum.wav') 
    instance.vlm_set_loop('drum.wav', True)
    print(instance.vlm_set_loop('drum.wav', True))
    p.set_media(m)
    p.play()
    is_playing = True
    is_paused = False
    last_position = None
    button_held = False
    encoder = rotaryio.IncrementalEncoder(seesaw)
    volume = 100

    while True: 
        if my_button.is_button_pressed() == True:
            p.pause()
            is_playing = False
            is_paused = not is_paused
            time.sleep(0.2)

        elif not is_playing and not is_paused:    
            p.play()
            is_playing = True

        # negate the position to make clockwise rotation positive
        position = encoder.position

        if position != last_position:
            last_position = position
            print("Position: {}".format(position))
            if -20 <= position and position <= 20:
                vlc.libvlc_audio_set_volume(p, volume + position * 5)
                print("Volume: {}".format(volume + position * 5))

        if not button.value and not button_held:
            button_held = True
            print("Button pressed")

        if button.value and button_held:
            button_held = False
            print("Button released")
        
        
if __name__ == '__main__':
    try:
        run_example()
    except (KeyboardInterrupt, SystemExit) as exErr:
        sys.exit(0)