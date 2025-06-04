from algorithm import build_frequency_dict, build_tree, build_codebook, encode, decode

input_text = "TO BE OR NOT TO BE"
n = 1  # n-grams

print(f"Input text: {input_text}\nSelected n-gram size: {n}")

# 1. Generate n-grams and count frequencies
n_grams = [input_text[i:i + n] for i in range(0, len(input_text), n)]
frequency_dict = build_frequency_dict(n_grams)

print("\nFrequencies:")
for symbol, freq in frequency_dict.items():
    print(f"'{symbol}': {freq}")

# 2. Build Huffman tree and codebook
root = build_tree(frequency_dict)
codebook = build_codebook(root)

print("\nCodebook:")
for symbol, code in codebook.items():
    print(f"'{symbol}': {code}")

# 3. Encode the message
encoded = encode(input_text, codebook, n)
print(f"\nEncoded text:\n{encoded}")

# 4. Decode the message
decoded = decode(encoded, root)
print(f"\nDecoded text:\n{decoded}")
