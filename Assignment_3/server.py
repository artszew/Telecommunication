import socket
import pickle  # module for serialization
from algorithm import build_tree, decode

HOST = '0.0.0.0'  # listen on all interfaces
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("Server is listening...")

    connection, address = s.accept()
    with connection:
        print(f"Connected to: {address}")
        data = b""
        while True:
            packet = connection.recv(4096)
            if not packet:
                break
            data += packet

        # receive data as dictionary (pickle)
        received_data = pickle.loads(data)
        encoded = received_data['encoded']
        tree_data = received_data['tree_data']

        # rebuild tree and decode
        root = build_tree(tree_data)
        decoded_text = decode(encoded, root)

        # save result
        with open("decoded_output.txt", "w", encoding="utf-8") as f:
            f.write(decoded_text)

        print("Saved as decoded_output.txt")

