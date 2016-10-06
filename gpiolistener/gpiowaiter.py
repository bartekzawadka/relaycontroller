from threading import Thread
import time


class GpioWaiter(Thread):

    def __init__(self, relay_alive_time ,waiting_finished_callback):
        self.IS_RUNNING = False
        self.__waiting_finished_callback = waiting_finished_callback
        self.relay_alive_time = relay_alive_time
        Thread.__init__(self)

    def stop(self):
        self.IS_RUNNING = False

    def run(self):
        self.IS_RUNNING = True
        time.sleep(self.relay_alive_time * 60)
        self.IS_RUNNING = False
        self.__waiting_finished_callback()