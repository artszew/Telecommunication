import socket
import pickle
from algorithm import build_frequency_dict, build_tree, build_codebook, encode

HOST = 'xyz.xyz.xy.xyz'  # host
PORT = 65432

filename = "message.txt"
n = 1  # n-gram


# read file
with open(filename, "r", encoding="utf-8") as f:
    text = f.read()

n_grams = [text[i:i + n] for i in range(0, len(text), n)]
freq_dict = build_frequency_dict(n_grams)
root = build_tree(freq_dict)
codebook = build_codebook(root)
encoded = encode(text, codebook, n)

# serialization
payload = {
    'encoded': encoded,
    'tree_data': freq_dict
}

serialized = pickle.dumps(payload)

# send via socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(serialized)

print("Encoded text sent.")
