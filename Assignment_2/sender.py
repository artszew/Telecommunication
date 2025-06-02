# python sender.py --port COM6 --file to_send.txt --crc
import serial
import time
import argparse

# Global constants and checksum/CRC helper functions
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

def send_file(port_name, file_path, use_crc):
    with serial.Serial(port_name, baudrate=9600, timeout=TIMEOUT) as ser:
        print(f"[INFO] Waiting for receiver initialization ({'CRC' if use_crc else 'Checksum'})...")
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        start_time = time.time()
        while time.time() - start_time < 60:
            init_byte = ser.read(1)
            if init_byte and init_byte[0] in [NAK, C]:
                use_crc = init_byte[0] == C
                print("[INFO] Initialization received.")
                break
        else:
            print("[ERROR] No response from receiver.")
            return

        with open(file_path, 'rb') as f:
            block_num = 1

            while True:
                block = f.read(BLOCK_SIZE)
                if not block:
                    break  # EOF

                block = block.ljust(BLOCK_SIZE, b'\x1A')
                packet = bytearray([SOH, block_num, 255 - block_num]) + block

                if use_crc:
                    crc = calculate_crc16(block)
                    packet += crc.to_bytes(2, 'big')
                else:
                    checksum = calculate_checksum(block)
                    packet.append(checksum)

                for retry in range(MAX_RETRIES):
                    ser.write(packet)
                    ser.flush()
                    time.sleep(0.1)
                    response = ser.read(1)
                    if response and response[0] == ACK:
                        print(f"[INFO] Block {block_num} sent successfully.")
                        block_num = (block_num + 1) % 256
                        break
                    elif response and response[0] == NAK:
                        print(f"[WARN] NAK for block {block_num}, retrying...")  # Retransmission
                else:
                    print("[ERROR] Maximum number of retries exceeded.")
                    return

        # Send EOT
        for _ in range(MAX_RETRIES):
            ser.write(bytes([EOT]))
            ser.flush()
            time.sleep(0.1)
            response = ser.read(1)
            if response and response[0] == ACK:
                print("[INFO] Transmission successfully completed (ACK after EOT).")
                return
            else:
                print("[WARN] Retrying EOT...")
        print("[ERROR] Failed to complete transmission.")

# Main
parser = argparse.ArgumentParser(description='Xmodem Sender')
parser.add_argument('--port', required=True, help='Serial port (e.g., COM3)')
parser.add_argument('--file', required=True, help='File to send')
parser.add_argument('--crc', action='store_true', help='Use CRC instead of simple checksum')
args = parser.parse_args()

send_file(args.port, args.file, args.crc)
