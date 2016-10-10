#!/usr/bin/env python
# -*- coding: utf-8 -*-
from threading import Thread
import RPi.GPIO as GPIO
import time
import signal
from gpiowaiter import GpioWaiter
from relaylogger import RelayLogger


def handle_sigterm():
    GPIO.cleanup()
signal.signal(signal.SIGTERM, handle_sigterm)


class GpioListener(Thread):

    STATE_COUNTING = 1
    STATE_OFF = 2
    STATE_PERMANENT_ON = 3

    def __init__(self):
        self.__read_config_file()
        self.__is_turned_on = False
        self.__continue_counting = True
        self.__waiter = None
        self.__current_state = GpioListener.STATE_PERMANENT_ON
        self.__states = [
            { "name": "W trakcie odliczania", "value": GpioListener.STATE_COUNTING},
            { "name": "Wylaczona", "value": GpioListener.STATE_OFF},
            { "name": "Wlaczona na stale", "value" : GpioListener.STATE_PERMANENT_ON}
        ]
        Thread.__init__(self)

    def __read_config_file(self):
        conf = {}
        execfile("/home/pi/relaycontroller/config/relaycontroller.conf", conf)
        self.input_signal_gpio_port = conf["input_signal_gpio_port"]
        self.relay_control_gpio_port = conf["relay_control_gpio_port"]
        self.relay_alive_time = conf["relay_alive_time"]
        self.logs_dir = conf["logs_dir"]

    def __configure_gpio(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.relay_control_gpio_port, GPIO.OUT)

    def __waiting_finished(self):
        GPIO.output(self.relay_control_gpio_port, False)
        self.set_state(GpioListener.STATE_OFF)

    def set_relay_alive_time(self, minutes):
        filedata = None
        with open('/home/pi/relaycontroller/config/relaycontroller.conf', 'r') as file:
            filedata = file.read()

        filedata = filedata.replace('relay_alive_time = %s' % self.relay_alive_time, 'relay_alive_time = %s' % minutes)

        with open('/home/pi/relaycontroller/config/relaycontroller.conf', 'w') as file:
            file.write(filedata)

        self.relay_alive_time = minutes

    def get_relay_alive_time(self):
        return self.relay_alive_time

    def get_states(self):
        return self.__states

    def get_state(self):
        for x in self.__states:
            if x["value"] == self.__current_state:
                return x["value"]

    def set_relay_timeout(self, minutes):
        if self.__waiter is not None and self.__waiter.IS_RUNNING is True:
            self.__waiter.stop()
        time.sleep(1)
        self.set_relay_alive_time(minutes)

    def stop(self):
        # TODO: Stop thread, stop counter
        self.__is_turned_on = False
        GPIO.cleanup()

    def set_state(self, state):
        self.__current_state = state

    def run(self):
        try:
            self.__is_turned_on = True
            self.__configure_gpio()
            self.set_state(GpioListener.STATE_PERMANENT_ON)
            RelayLogger.get_logger("relaycontroller", self.logs_dir).info("Started listening on GPIO port %s" %
                                                                        self.input_signal_gpio_port)

            while self.__is_turned_on is True:
                if self.__current_state is GpioListener.STATE_PERMANENT_ON:
                    if GPIO.input(self.relay_control_gpio_port) is 0:
                        GPIO.output(self.relay_control_gpio_port, True)
                elif self.__current_state is GpioListener.STATE_OFF and GPIO.input(self.relay_control_gpio_port) is 1:
                    GPIO.output(self.relay_control_gpio_port, False)
                elif self.__current_state is GpioListener.STATE_COUNTING:
                    if self.__waiter is None or self.__waiter.IS_RUNNING is False or GPIO.input(self.relay_control_gpio_port) is 0:
                        RelayLogger.get_logger("Relay Service", self.logs_dir)\
                            .info("Counting command received. Relay is going to be alive for next %s minutes" %
                                         self.relay_alive_time)
                        GPIO.output(self.relay_control_gpio_port, True)
                        self.__waiter = GpioWaiter(self.relay_alive_time, self.__waiting_finished)
                        self.__waiter.start()
                time.sleep(0.1)
        except Exception, e:
            RelayLogger.get_logger("relaycontroller", self.logs_dir) \
                .error("Unexpected error occurred while listener thread was working:\n%s" % e)
        finally:
            GPIO.cleanup()