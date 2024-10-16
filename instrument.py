import time
import serial
import queue
from threading import Thread
from sys import exc_info

# Delays used to help communication
delay_before_write = 0.005  # time to wait before sending a command
delay_before_read = 0.005  # time to wait before reading response
delay_queue = 0.1  # how periodically (in seconds) the queue is checked for messages
default_comports = ('COM6', 'COM7')  # iTC first, iPS second
default_baudrate = 115200
default_timeout = 0.25
default_stopbits = serial.STOPBITS_TWO
default_bytesize = serial.EIGHTBITS
default_parity = serial.PARITY_NONE


class SerialMessage:
    """
    A message to be submitted into the queue of an open serial port. Initializing the object creates a message to be
    sent. The `print_response' flag dictates whether to print the message and response to std_out. The response()
    method waits for a response from the instrument: a (default) timeout == 0 waits up to 60 s, and a timeout != 0
    specifies a maximum time in seconds to wait for a response.
    """
    def __init__(self, message, print_response=True):
        self.message = message
        self.print_response = print_response
        self._response = None

    def response(self, timeout=0):
        if not timeout:
            timeout = 60
        start_time = time.time()
        while time.time() - start_time <= timeout:  # allow up to `timeout' seconds for a response
            if self._response is not None:
                break
            time.sleep(0.01)  # don't hog the computer
        return self._response


class SerialPort:
    """
    An object that manages communication through a single serial port. A queue is used to prevent timing clashes of
    messages being sent/received, and a thread is used to monitor this queue for new entries. The queue is populated
    by SerialMessage objects. When the thread detects a SerialMessage object in the queue, it sends the requested
    message, updates the object with the response, then moves on to the next object in the queue (if any).
    """
    def __init__(self):
        self.port = ''
        self.is_open = False
        self._serial = serial.Serial()
        self._thread = Thread()
        self._queue = queue.Queue()

    def __del__(self):
        if self._serial.is_open:
            try:
                self._serial.close()
            except serial.SerialException:
                print(f'Destructor error closing COM port: {exc_info()[0]}\a')

    def _serial_io_thread(self):
        """
        A daemon thread function that continuously waits for messages to appear in the queue. When it receives a new
        message, it sends it to the serial port and returns the response to the SerialMessage object.
        """
        while True:
            if self.is_open:  # ensure the serial connection is still open
                try:  # check if there is an entry in the queue
                    serialmessage = self._queue.get(False)
                except queue.Empty:  # otherwise wait `delay' seconds then retry
                    time.sleep(delay_queue)
                    continue
                if isinstance(serialmessage, SerialMessage):
                    newmessage = serialmessage.message.strip() + '\n'
                    try:
                        time.sleep(delay_before_write)
                        self._serial.write(newmessage.encode('utf-8'))
                    except ValueError:
                        print(f'Error sending, ValueError:{newmessage[:-2]},{exc_info()[0]}\a')
                        serialmessage._response = '~'  # flag sending error
                    except serial.SerialException:
                        print(f'Error sending, SerialException:{newmessage[:-2]},{exc_info()[0]}\a')
                        serialmessage._response = '~'  # flag sending error
                    else:
                        time.sleep(delay_before_read)
                        response = self._serial.readline()
                        if response is not None:
                            response = response.decode('utf-8').strip('\n')
                        else:
                            response = ''
                        if serialmessage.print_response:
                            print(newmessage[:-2], response)
                        serialmessage._response = response
                elif isinstance(serialmessage, str):
                    newmessage = serialmessage.message.strip() + '\n'
                    try:
                        time.sleep(delay_before_write)
                        self._serial.write(newmessage.encode('utf-8'))
                    except ValueError:
                        print(f'Error sending, ValueError:{newmessage[:-2]},{exc_info()[0]}\a')
                    except serial.SerialException:
                        print(f'Error sending, SerialException:{newmessage[:-2]},{exc_info()[0]}\a')
                    else:
                        time.sleep(delay_before_read)
                        response = self._serial.readline().decode('utf-8').strip('\n')
                        print(newmessage[:-2], response)
                else:
                    raise TypeError
            else:
                break

    def open(self, portname=None):
        """
        Opens a connection to the serial port using the default baud rate and timeout settings from global variables.
        If `portname' is provided, this is the COM port name used; otherwise, self.Port is used. Upon establishing the
        connection, it initiates a queueing thread and returns True. If a connection fails or is already open, it
        returns False.
        """
        if not self.is_open:
            self._serial.port = portname if portname is not None else self.port
            self._serial.baudrate = default_baudrate
            self._serial.timeout = default_timeout
            self._serial.stopbits = default_stopbits
            self._serial.bytesize = default_bytesize
            self._serial.parity = default_parity
            try:
                self._serial.open()
            except serial.SerialException:
                print(f'Error opening COM port: {self._serial.port},{exc_info()[0]}\a')
                return False
            else:
                self.is_open = True
                self._thread = Thread(target=self._serial_io_thread, daemon=True)
                self._thread.start()
                return True
        return False

    def close(self):
        if self.is_open:
            try:
                self.is_open = False  # this flag will also cause the IO thread to quit
                self._serial.close()
                return True
            except serial.SerialException:
                print(f'Error closing COM port: {self._serial.port},{exc_info()[0]}\a')
                return False
        return False

    def transmit(self, message, error_message=None, print_response=True, attempts=2):
        while attempts > 0:
            transmission = SerialMessage(message, print_response)
            self._queue.put(transmission)
            response = transmission.response()
            if isinstance(response, str):
                if len(response) > 0:
                    if response[0] != '?':
                        break  # if responded without confusion
            self._serial.readline()
            attempts = attempts - 1
        if isinstance(response, str):
            if len(response) > 0:
                if response[0] == '?' and error_message is not None:
                    print(error_message)
            return response
        else:
            if error_message is not None:
                print(error_message)
            return '?'

if __name__ == '__main__':
    pass
