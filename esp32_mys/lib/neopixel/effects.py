import machine
from lib.utils import millis
from lib.utils import constrain
from lib.neopixel.constants import *


class WS2812FX(machine.Neopixel):
    def __init__(self, data_pin=DEFAULT_DATA_PIN, led_count=DEFAULT_PIXEL_COUNT, type=machine.Neopixel.TYPE_RGB):
        super().__init__(machine.Pin(data_pin), led_count, type)
        self._running = False
        self._triggered = False
        self._mode_index = DEFAULT_MODE
        self._speed = DEFAULT_SPEED
        self._brightness = DEFAULT_BRIGHTNESS
        self._led_count = led_count
        self._mode_last_call_time = 0
        self._mode_delay = 0
        self._color = DEFAULT_COLOR
        self._mode_color = DEFAULT_COLOR
        self._counter_mode_call = 0
        self._counter_mode_step = 0
        self._mode = {
            FX_MODE_STATIC: self.mode_static,
            FX_MODE_BLINK: self.mode_blink,
            FX_MODE_COLOR_WIPE: self.mode_color_wipe,
            # FX_MODE_COLOR_WIPE_RANDOM: self.mode_color_wipe_random,
            # FX_MODE_BREATH: self.mode_breath,
            # FX_MODE_RANDOM_COLOR: self.mode_random_color,
            # FX_MODE_SINGLE_DYNAMIC: self.mode_single_dynamic,
            # FX_MODE_MULTI_DYNAMIC: self.mode_multi_dynamic,
            # FX_MODE_RAINBOW: self.mode_rainbow,
            # FX_MODE_RAINBOW_CYCLE: self.mode_rainbow_cycle,
            # FX_MODE_SCAN: self.mode_scan,
            # FX_MODE_DUAL_SCAN: self.mode_dual_scan,
            # FX_MODE_FADE: self.mode_fade,
            # FX_MODE_THEATER_CHASE: self.mode_theater_chase,
            # FX_MODE_THEATER_CHASE_RAINBOW: self.mode_theater_chase_rainbow,
            # FX_MODE_RUNNING_LIGHTS: self.mode_running_lights,
            # FX_MODE_TWINKLE: self.mode_twinkle,
            # FX_MODE_TWINKLE_RANDOM: self.mode_twinkle_random,
            # FX_MODE_TWINKLE_FADE: self.mode_twinkle_fade,
            # FX_MODE_TWINKLE_FADE_RANDOM: self.mode_twinkle_fade_random,
            # FX_MODE_SPARKLE: self.mode_sparkle,
            # FX_MODE_FLASH_SPARKLE: self.mode_flash_sparkle,
            # FX_MODE_HYPER_SPARKLE: self.mode_hyper_sparkle,
            # FX_MODE_STROBE: self.mode_strobe,
            # FX_MODE_STROBE_RAINBOW: self.mode_strobe_rainbow,
            # FX_MODE_MULTI_STROBE: self.mode_multi_strobe,
            # FX_MODE_BLINK_RAINBOW: self.mode_blink_rainbow,
            # FX_MODE_CHASE_WHITE: self.mode_chase_white,
            # FX_MODE_CHASE_COLOR: self.mode_chase_color,
            # FX_MODE_CHASE_RANDOM: self.mode_chase_random,
            # FX_MODE_CHASE_RAINBOW: self.mode_chase_rainbow,
            # FX_MODE_CHASE_FLASH: self.mode_chase_flash,
            # FX_MODE_CHASE_FLASH_RANDOM: self.mode_chase_flash_random,
            # FX_MODE_CHASE_RAINBOW_WHITE: self.mode_chase_rainbow_white,
            # FX_MODE_CHASE_BLACKOUT: self.mode_chase_blackout,
            # FX_MODE_CHASE_BLACKOUT_RAINBOW: self.mode_chase_blackout_rainbow,
            # FX_MODE_COLOR_SWEEP_RANDOM: self.mode_color_sweep_random,
            # FX_MODE_RUNNING_COLOR: self.mode_running_color,
            # FX_MODE_RUNNING_RED_BLUE: self.mode_running_red_blue,
            # FX_MODE_RUNNING_RANDOM: self.mode_running_random,
            # FX_MODE_LARSON_SCANNER: self.mode_larson_scanner,
            # FX_MODE_COMET: self.mode_comet,
            # FX_MODE_FIREWORKS: self.mode_fireworks,
            # FX_MODE_FIREWORKS_RANDOM: self.mode_fireworks_random,
            # FX_MODE_MERRY_CHRISTMAS: self.mode_merry_christmas,
            # FX_MODE_FIRE_FLICKER: self.mode_fire_flicker,
            # FX_MODE_FIRE_FLICKER_SOFT: self.mode_fire_flicker_soft
        }

    def init(self):
        # could do super().brightness(...) also but we have a property called brightness also so there will be a conflict
        super().brightness(DEFAULT_BRIGHTNESS)
        self.show()

    def service(self):
        if self._running or self._triggered:
            now = millis()

            if (now - self._mode_last_call_time) > self._mode_delay or self._triggered:
                self._mode[self._mode_index]
                self._counter_mode_call = self._counter_mode_call + 1
                self._mode_last_call_time = now
                self._triggered = False

    def start(self):
        self._counter_mode_call = 0
        self._counter_mode_step = 0
        self._mode_last_call_time = 0
        self._running = True

    def stop(self):
        self._running = False
        self.strip_off()

    def trigger(self):
        self._triggered = True

    def set_mode(self, mode):
        self._counter_mode_call = 0
        self._counter_mode_step = 0
        self._mode_last_call_time = 0
        self._mode_index = constrain(mode, 0, MODE_COUNT-1)
        self._mode_color = self._color
        super().brightness(self._brightness)

    def set_speed(self, speed):
        self._counter_mode_call = 0
        self._counter_mode_step = 0
        self._mode_last_call_time = 0
        self._speed = constrain(speed, SPEED_MIN, SPEED_MAX)

    def increase_speed(self, speed):
        self.set_speed(constrain(self._speed + speed, SPEED_MIN, SPEED_MAX))

    def decrease_speed(self, speed):
        self.set_speed(constrain(self._speed - speed, SPEED_MIN, SPEED_MAX))

    def set_color(self, color):
        self._color = color
        self._counter_mode_call = 0
        self._counter_mode_step = 0
        self._mode_last_call_time = 0
        self._mode_color = self._color
        super().brightness(self._brightness)

    def set_color_index(self, r_index, g_index, b_index):
        self.set_color((r_index << 16) | (g_index << 8) | b_index)

    def set_brightness(self, brightness):
        self._brightness = constrain(brightness, BRIGHTNESS_MIN, BRIGHTNESS_MAX)
        super().brightness(self._brightness)
        self.show()

    def increase_brightness(self, brightness):
        self.set_brightness(constrain(self._brightness + brightness, BRIGHTNESS_MIN, BRIGHTNESS_MAX))

    def decrease_brightness(self, brightness):
        self.set_brightness(constrain(self._brightness - brightness, BRIGHTNESS_MIN, BRIGHTNESS_MAX))

    def strip_off(self):
        self.clear()
        self.show()

    def color_wheel(self, pos):
        pos = 255 - pos
        if pos < 85:
            return ((255 - pos * 3) << 16) | (0 << 8) | (pos * 3)
        elif pos < 170:
            pos -= 85
            return (0 << 16) | ((pos * 3) << 8) | (255 - pos * 3)
        else:
            pos -= 170
            return ((pos * 3) << 16) | ((255 - pos * 3) << 8) | 0

    def get_random_wheel_index(self, pos):
        r = 0
        x = 0
        y = 0
        d = 0

        while d < 42:
            r = machine.random(256)
            x = abs(pos - r)
            y = 255 - x
            d = min(x, y)

        return r

    def mode_static(self):
        self.set(0, self._color, num=self._led_count)
        self.show()
        self._mode_delay = 50

    def mode_blink(self):
        if self._counter_mode_call % 2 == 1:
            self.set(0, self._color, num=self._led_count)
            self.show()
        else:
            self.strip_off()
        self._mode_delay = 100 + ((1986 * (SPEED_MAX - self._speed)) / SPEED_MAX)

    def mode_color_wipe(self):
        if self._counter_mode_step < self._led_count:
            self.set(self._counter_mode_step, self._color)
        else:
            self.set(self._counter_mode_step - self._led_count, 0)
        self.show()
        self._counter_mode_step = (self._counter_mode_step + 1) % (self._led_count * 2)
        self._mode_delay = 5 + ((50 * (SPEED_MAX - self._speed)) / self._led_count)

    @property
    def running(self):
        return self._running

    @property
    def mode(self):
        return self._mode

    @property
    def speed(self):
        return self._speed

    @property
    def brightness(self):
        return self._brightness

    @property
    def mode_count(self):
        return len(self._mode)

    @property
    def color(self):
        return self._color
