import board
import displayio
import time
from adafruit_clue import clue
from simpleio import map_range
from adafruit_bitmap_font import bitmap_font
from adafruit_lsm6ds.lsm6ds33 import LSM6DS33
from adafruit_lsm6ds import Rate, AccelRange
from adafruit_display_text.label import Label

#accessing the board's accelerometer
sensor = LSM6DS33(board.I2C())

#step goal
step_goal = 1000

#onboard button states for btn debouncing
upper_state = False
lower_state = False



cntdown = 0 #variable for the step progress bar
clock = 0 #variable used to keep track of time for the sph counter
clock_count = 0 #number of hours that the step counter has been running
clock_check = 0 #result of the clock divided by 3600 seconds
last_step = 0 #state used to properly counter steps
mono = time.monotonic()
mode = 1 #screen brightness
steps_log = 0 #total steps to check for steps per hour
steps_remaining = 0 #remaining steps needed to reach the step goal
sph = 0 #steps per hour

clue_bgBMP = "/logo.bmp"
_font = "/font/Roboto-Medium-16.bdf"

#loading bitmap font
_font = bitmap_font.load_font(_font)
_font.load_glyphs(glyphs)

#creating display and default brightness
clue_display = board.DISPLAY
clue_display.brightness = 0.5
#array to adjust screen brightness
bright_level = [0, 0.5, 1]

#graphics
clueGroup = displayio.Group(max_size=30)

#loading bitmap background
clue_bg = displayio.OnDiskBitmap(open(clue_bgBMP, "rb"))
clue_tilegrid = displayio.TileGrid(clue_bg, pixel_shader=getattr(clue_bg, 'pixel_shader', displayio.ColorConverter()))
clueGroup.append(clue_tilegrid)

#creating the progress bar
bar_group = displayio.Group(max_size=20)
prog_bar = ProgressBar(1, 1, 239, 25, bar_color=0x652f8f)
bar_group.append(prog_bar)

clueGroup.append(bar_group)
#text for steps
text_steps = Label(big_font, text="0     ", color=0xe90e8b)
text_steps.x = 50
text_steps.y = 75

#text 
text_sph = Label(med_font, text=" -- ", color=0x29abe2)
text_sph.x = 10
text_sph.y = 200
steps_cntdown = Label(_font, text='%d Steps Remaining' % step_goal, color=clue.WHITE)
steps_cntdown.x = 60
steps_cntdown.y = 15



#adding all text to the display group
clueGroup.append(steps_cntdown)
clueGroup.append(text_steps)
clueGroup.append(text_sph)
clue_display.show(clueGroup)

#setting up the accelerometer and pedometer
sensor.gyro_data_rate = Rate.RATE_SHUTDOWN
sensor.pedometer_enable = True
sensor.accelerometer_range = AccelRange.RANGE_2G
sensor.accelerometer_data_rate = Rate.RATE_26_HZ

while True:

    #signal debouncing
    if not clue.button_a and not upper_state:
        upper_state = True
    if not clue.button_b and not lower_state:
        lower_state = True

    #setting up steps for step count
    steps = sensor.pedometer_steps

    #creating data for the progress bar
    cntdown = map_range(steps, 0, step_goal, 0.0, 1.0)

    #counting of the steps
    #if a step is taken:
    if abs(steps-last_step) > 1:
        step_time = time.monotonic()
        #updates last_step
        last_step = steps
        #updates the display
        text_steps.text = '%d' % steps
        clock = step_time - mono

        #logging steps per hour
        if clock > 3600:
            #gets number of hours to add to total
            clock_check = clock / 3600
            #logs the step count as of that hour
            steps_log = steps
            #adds the hours to get a new hours total
            clock_count += round(clock_check)
            #divides steps by hours to get steps per hour
            sph = steps_log / clock_count
            text_sph.text = '%d' % sph
            #reset
            clock = 0
            mono = time.monotonic()

        #cntdown to step goal
        prog_bar.progress = float(cntdown)

    #displaying cntdown to step goal
    if step_goal - steps > 0:
        steps_remaining = step_goal - steps
        steps_cntdown.text = '%d Remaining Steps' % steps_remaining
    else:
        steps_cntdown.text = 'Step Goal Met'

    #adjusting screen brightness, a button decreases brightness
    if clue.button_a and upper_state:
        mode -= 1
        upper_state = False
        if mode < 0:
            mode = 0
            clue_display.brightness = bright_level[mode]
        else:
            clue_display.brightness = bright_level[mode]
    #adjusting screen brightness, b button increases brightness
    if clue.button_b and lower_state:
        mode += 1
        lower_state = False
        clue_display.brightness = bright_level[mode]

    time.sleep(0.01)
