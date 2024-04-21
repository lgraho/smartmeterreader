import sys
from collections import namedtuple
import logging
import struct
from binascii import hexlify, unhexlify
from Crypto.Cipher import AES

Frame = namedtuple("Frame", "system_title frame_counter data")
DataItem = namedtuple("DataItem", "value scale unit")

class Parser():
    """
    Represents a parser for extracting data from M-Bus frames.

    Attributes:
        key (str): The encryption key used to decrypt the data.
        system_title_slice (slice): The slice of the frame containing the system title.
        frame_counter_slice (slice): The slice of the frame containing the frame counter.
        data_slice (slice): The slice of the frame containing the encrypted data.
        apdu_format (dict): The format of the APDU data.
    """
    def __init__(self, key: str, frame_format: dict, apdu_format: dict):
        logging.info("Initializing parser...")
        try:
            self.key = unhexlify(key)
        except ValueError:
            logging.error("Failed initializing parser: Invalid encryption key")
            sys.exit("Invalid encryption key")
        self.system_title_slice = slice(frame_format["system_title"]["start"], frame_format["system_title"]["end"])
        self.frame_counter_slice = slice(frame_format["frame_counter"]["start"], frame_format["frame_counter"]["end"])
        self.data_slice = slice(frame_format["data"]["start"], frame_format["data"]["end"])
        self.apdu_format = apdu_format

    def _slice_frame(self, frame: bytes) -> Frame:
        return Frame(frame[self.system_title_slice], frame[self.frame_counter_slice], frame[self.data_slice])

    def _decrypt(self, data: bytes, init_vector: bytes) -> bytes:
        cipher = AES.new(self.key, AES.MODE_GCM, nonce=init_vector)
        decrypted_data = cipher.decrypt(data)
        return decrypted_data

    def _parse(self, apdu: bytes) -> dict:
        data = {}
        for field in self.apdu_format:
            try:
                item = self._extract_item(apdu, field)
                value = item.value * 10**item.scale
                if isinstance(value, float):
                    value = round(value, 3)
                data[field["name"]] = value
            except ValueError:
                logging.error("Failed parsing APDU: Could not extract '%s' (OBIS: %s)", field["name"], field["obis"])
                logging.debug("APDU: %s", hexlify(bytearray(apdu)))
                return None
        return data

    def _extract_item(self, apdu: bytes, field: dict) -> DataItem:
        index = apdu.index(bytes.fromhex(field["obis"]))
        field_size = struct.calcsize(field["format"])
        item = DataItem._make(struct.unpack_from(field["format"], apdu[index:index+field_size]))
        logging.debug("Extracted data item: %s", item)
        return item

    def extract_data(self, frame: bytes) -> dict:
        """
        Extracts data from an M-Bus frame.

        Args:
            frame (bytes): The M-Bus frame to extract data from.

        Returns:
            dict: A dictionary containing the extracted data.
        """
        f = self._slice_frame(frame)
        init_vector = f.system_title + f.frame_counter
        decrypted_apdu = self._decrypt(f.data, init_vector)
        data = self._parse(decrypted_apdu)
        logging.debug("Extracted data: %s", data)
        return data