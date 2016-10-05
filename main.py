from relayservice import RelayService
import signal
import RPi.GPIO as GPIO


def handle_sigterm():
    GPIO.cleanup()
signal.signal(signal.SIGTERM, handle_sigterm)

if __name__ == '__main__':
    rs = RelayService()
    rs.start_listener()