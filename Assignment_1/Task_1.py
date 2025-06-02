import random

while True:
    option = int(input("Choose option: 1 - single error, 2 - double error: "))
    if option not in (1, 2):
        print("Invalid option, ending program.")
        continue

    message = input("Enter 8-bit message: ")
    T = [int(ch) for ch in message.strip()]  # message bits

    if option == 1:  # single error
        H = [  # parity matrix
            [1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0],  # h11,...,h18,c1,...,c4
            [1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0],
            [1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0],
            [0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1]
        ]
    else:  # double error
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

    # encoding
    rows = len(H)
    T = T + [sum(H[n][m] * T[m] for m in range(8)) % 2 for n in range(rows)]
    print("Encoded message T =", ''.join(map(str, T)))

    # introduce errors
    error_positions = random.sample(range(1, 9), option)  # random bit positions
    for pos in error_positions:
        T[pos - 1] = 1 - T[pos - 1]  # simulate error
    print(f"Message with simulated error at position(s) {error_positions}: T = ", ''.join(map(str, T)))

    # error vector
    E = [sum(H[i][j] * T[j] for j in range(len(T))) % 2 for i in range(rows)]
    print(f"Error vector E =", ''.join(map(str, E)))

    # error correction
    columns = len(H[0])
    if option == 1:
        for m in range(columns):
            if all(H[n][m] == E[n] for n in range(rows)):
                T[m] = 1 - T[m]  # correct error
                break
    else:
        for n in range(columns):
            for m in range(n + 1, columns):
                if all((H[k][n] ^ H[k][m]) == E[k] for k in range(rows)):
                    T[n] = 1 - T[n]
                    T[m] = 1 - T[m]
                    break

    print("Message after error detection and correction:", ''.join(map(str, T)))

    if input("\nDo you want to continue the program? (Y/N): ").upper() != 'Y':
        break
