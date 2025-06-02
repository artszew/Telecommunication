while True:
    print("\nChoose an option:",
          "\n1 - Encoding (your file -> encoded.txt)",
          "\n2 - Decoding (encoded.txt -> decoded.txt)")
    option = input("Your choice: ").strip()

    # Parity check matrix H for 17-bit codeword (8 data bits + 9 parity bits)
    H = [
        [1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    ]

    rows = len(H)
    cols = len(H[0])

    if option == "1":  # Encoding
        file_name = input("Enter the name of the file to encode the message from: ")
        with open(file_name, "r", encoding="utf-8") as input_file, open("encoded.txt", "w") as encoded_file:
            for line in input_file:
                line = line.rstrip("\n")
                for ch in line:
                    binary = format(ord(ch), '08b')
                    T = [int(b) for b in binary]
                    # Add parity bits
                    T += [sum(H[r][j] * T[j] for j in range(8)) % 2 for r in range(rows)]

                    encoded_file.write(''.join(str(bit) for bit in T) + "\n")

        print("Encoding complete. Result saved in 'encoded.txt'.")

    elif option == "2":  # Decoding
        with open("encoded.txt", "r") as encoded_file, open("decoded.txt", "w", encoding="utf-8") as decoded_file:
            for line in encoded_file:
                line = line.strip()
                if len(line) != cols or not set(line).issubset({'0', '1'}):
                    continue  # Skip invalid lines

                T = [int(b) for b in line]

                # Calculate the error syndrome
                E = [sum(H[i][j] * T[j] for j in range(cols)) % 2 for i in range(rows)]

                if any(E):  # Error detected
                    corrected = False

                    # Try single-bit error correction
                    for m in range(cols):
                        if all(H[n][m] == E[n] for n in range(rows)):
                            T[m] = 1 - T[m]
                            corrected = True
                            break

                    # Try double-bit error correction
                    if not corrected:
                        for n in range(cols):
                            for m in range(n + 1, cols):
                                if all((H[k][n] ^ H[k][m]) == E[k] for k in range(rows)):
                                    T[n] = 1 - T[n]
                                    T[m] = 1 - T[m]
                                    corrected = True
                                    break
                            if corrected:
                                break

                # Extract the original 8-bit character
                decoded_char = chr(int(''.join(str(bit) for bit in T[:8]), 2))
                decoded_file.write(decoded_char)

        print("Decoding complete. Result saved in 'decoded.txt'.")

    else:
        print("Invalid choice.")

    if input("\nDo you want to continue the program? (Y/N): ").strip().upper() != 'Y':
        break
