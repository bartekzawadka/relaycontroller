import RPi.GPIO as GPIO
import logging
import logging.handlers
import time
import os


class RelayService:
    def __init__(self):
        self.__read_config_file()
        self.__init_logger()

    def __init_logger(self):
        logger = logging.getLogger(name="Relay Service")
        logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

        handler = logging.handlers.TimedRotatingFileHandler(os.path.join(self.logs_dir, 'relayservice.log'), when="midnight")
        handler.suffix = "%Y-%m-%d"
        handler.setFormatter(formatter)

        logger.addHandler(handler)
        self.logger = logger

    def __read_config_file(self):
        # try:
        conf = {}
        execfile("/home/pi/relaycontroller/config/relayservice.conf", conf)
        self.input_signal_gpio_port = conf["input_signal_gpio_port"]
        self.relay_control_gpio_port = conf["relay_control_gpio_port"]
        self.relay_alive_time = conf["relay_alive_time"]
        self.logs_dir = conf["logs_dir"]
        # except Exception, e:
        #   self.logger.error("Error reading config file:\n%s" % e)

    def __input_event_callback(self, channel):
        self.logger.info("Input GPIO event detected! STATE: %s " % GPIO.input(self.input_signal_gpio_port))

    def start_listener(self):
        try:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.input_signal_gpio_port, GPIO.IN)
            GPIO.setup(self.relay_control_gpio_port, GPIO.OUT)

            self.logger.info("Started listening on GPIO port %s" % self.input_signal_gpio_port)

            last_state = GPIO.input(self.input_signal_gpio_port)
            self.logger.info("Start state: %s" % GPIO.input(self.input_signal_gpio_port))
            GPIO.output(self.relay_control_gpio_port, True)

            while True:
                if GPIO.input(self.input_signal_gpio_port) is 1 and GPIO.input(self.relay_control_gpio_port) is 0:
                    GPIO.output(self.relay_control_gpio_port, True)

                if last_state is 1 and GPIO.input(self.input_signal_gpio_port) is 0:
                    self.logger.info("Switch turned on. Relay is going to be alive for next %s minutes" %
                                     self.relay_alive_time)
                    GPIO.output(self.relay_control_gpio_port, True)
                    time.sleep(self.relay_alive_time*60)
                    GPIO.output(self.relay_control_gpio_port, False)
                last_state = GPIO.input(self.input_signal_gpio_port)

                time.sleep(0.1)
        finally:
            GPIO.cleanup()