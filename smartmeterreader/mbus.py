import logging
import serial
from binascii import hexlify

class MBus():
    """
    Represents an M-Bus device for reading data from a smart meter.

    Attributes:
        baudrate (int): The baud rate of the serial port connection.
        port (str): The serial port to which the M-Bus device is connected.
        frame_size (int): The size of an M-Bus frame in bytes.
        preamble (bytes): The preamble of an M-Bus frame used to identify the start of a frame.
    """

    def __init__(self, config: dict, frame_format: dict):
        """
        Initializes a new instance of the M-Bus class.

        Args:
            config (dict): The configuration of the M-Bus device.
            frame_format (dict): The format of the M-Bus frame.
        """
        logging.info("Initializing M-Bus...")
        self.baudrate = config["baudrate"]
        self.port = config["port"]
        self.frame_size = frame_format["frame_size"]
        self.preamble = bytes.fromhex(frame_format["preamble"])
        self.serial = serial.Serial(self.port, self.baudrate)
        self.serial.timeout = 3
        logging.info("Connected to M-Bus device on port %s with baud rate %d", self.port, self.baudrate)

    def read_frame(self) -> bytes:
        """
        Reads a complete M-Bus frame from the serial port. Blocks until a complete frame is received.

        Returns:
            bytes: The complete M-Bus frame.
        """
        # Read until preamble is found
        while True:
            data = self.serial.read(len(self.preamble))
            if len(data) < len(self.preamble):
                continue
            if data == self.preamble:
                # Read the rest of the frame
                data += self.serial.read(self.frame_size - len(self.preamble))
                if(len(data) != self.frame_size):
                    # frame incomplete -> try again
                    continue
                logging.debug("Received M-Bus frame: %s", hexlify(bytearray(data)))
                return data

    def close(self):
        """
        Closes the serial port connection.
        """
        self.serial.close()
        logging.info("Closed M-Bus connection")
