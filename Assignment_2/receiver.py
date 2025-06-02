# python receiver.py --port COM5 --out received.txt --crc

import serial
import time
import argparse

# Global constants and helper functions for checksum/CRC
SOH = 0x01
EOT = 0x04
ACK = 0x06
NAK = 0x15
CAN = 0x18
C   = 0x43

BLOCK_SIZE = 128
MAX_RETRIES = 10
TIMEOUT = 10

def calculate_checksum(data: bytes) -> int:
    return sum(data) % 256  # No complement

def calculate_crc16(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF  # Limit to 16 bits
    return crc

def receive_file(port_name, output_path, use_crc):
    with serial.Serial(port_name, baudrate=9600, timeout=TIMEOUT) as ser, open(output_path, 'wb') as out:
        print(f"[INFO] Sending {'C' if use_crc else 'NAK'} to initiate transmission...")
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        # Transmission initialization
        for _ in range(6):
            ser.write(bytes([C if use_crc else NAK]))
            ser.flush()
            if ser.in_waiting:
                print("[INFO] Sender is transmitting, stopping init sequence early and starting reception.")
                break
            time.sleep(10)

        expected_block = 1
        received_data = bytearray()
        while True:
            header = ser.read(3)
            if not header:
                continue

            if header[0] == EOT:
                ser.write(bytes([ACK]))
                ser.flush()
                time.sleep(0.1)
                print("[INFO] EOT received. Closing transmission. (ACK sent)")

                # Trim padding (\x1A) characters
                trimmed_data = received_data.rstrip(b'\x1A')
                out.write(trimmed_data)
                break

            if len(header) < 3 or header[0] != SOH:
                print("[WARN] Invalid header.")
                ser.write(bytes([NAK]))
                time.sleep(0.1)
                continue

            block_num, block_comp = header[1], header[2]
            if block_num + block_comp != 0xFF:
                print("[ERROR] Block number mismatch.")
                ser.write(bytes([NAK]))
                time.sleep(0.1)
                continue

            data = ser.read(BLOCK_SIZE)
            if use_crc:  # CRC mode
                crc_bytes = ser.read(2)
                received_crc = int.from_bytes(crc_bytes, 'big')
                calc_crc = calculate_crc16(data)
                valid = received_crc == calc_crc
            else:  # Checksum mode
                checksum = ser.read(1)[0]
                calc_sum = calculate_checksum(data)
                valid = checksum == calc_sum

            if valid and block_num == expected_block:
                received_data += data
                ser.write(bytes([ACK]))
                ser.flush()
                time.sleep(0.1)
                print(f"[INFO] Block {block_num} received successfully.")
                expected_block = (expected_block + 1) % 256
            else:
                ser.write(bytes([NAK]))

# Main
parser = argparse.ArgumentParser(description='Xmodem Receiver')
parser.add_argument('--port', required=True, help='Serial port (e.g., COM4)')
parser.add_argument('--out', required=True, help='Path to save the received file')
parser.add_argument('--crc', action='store_true', help='Use CRC instead of checksum during reception')
args = parser.parse_args()

receive_file(args.port, args.out, args.crc)  # Entry point
