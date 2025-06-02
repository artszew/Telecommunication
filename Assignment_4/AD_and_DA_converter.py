import sounddevice as sd
import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write, read
from scipy.signal import resample

# A/D
def record_audio(filename, duration=5, fs=44100, bits=16):
    print(f"Recording... ({duration}s, {fs} Hz, {bits} bits)")
    dtype = 'int' + str(bits)
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype=dtype)
    sd.wait()
    write(filename, fs, audio)
    print(f"Saved: {filename}")
    return audio.astype(np.float32), fs

# D/A
def play_audio(filename):
    fs, data = read(filename)
    print(f"Playing: {filename}")
    sd.play(data, fs)
    sd.wait()

def quantize(audio, bits):
    max_val = np.max(np.abs(audio))
    levels = 2 ** bits
    quantized = np.round((audio / max_val) * (levels / 2 - 1)) * (max_val / (levels / 2 - 1))
    return quantized

def resample_audio(audio, original_fs, new_fs):
    num_samples = int(len(audio) * new_fs / original_fs)
    return resample(audio, num_samples)

# Quality metrics
def calculate_snr(original, processed):
    noise = original - processed
    return 10 * np.log10(np.sum(original ** 2) / np.sum(noise ** 2))

def calculate_mse(original, processed):
    return np.mean((original - processed) ** 2)

# Plotting
def plot_results(results, ylabel, title):
    for fs in sorted(set(r[0] for r in results)):
        x = [r[1] for r in results if r[0] == fs]
        y = [r[2] for r in results if r[0] == fs]
        plt.plot(x, y, marker='o', label=f'{fs} Hz')
    plt.xlabel("Number of bits")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.show()

# Main
# Test settings
quantization_bits = [2, 3, 4, 6, 8, 12, 16]
sampling_rates = [8000, 16000, 22050, 44100]

print("-- Part 1 - Recording --")
try:
    duration = int(input("Warning, recording will start shortly. Enter duration in seconds: "))
except ValueError:
    print("Invalid input – default duration of 5 seconds will be used.\n")
    duration = 5

original_audio, base_fs = record_audio("original_base.wav", duration=duration, fs=44100, bits=16)

snr_results = []
mse_results = []
all_files = {}

print("\n-- Part 2 - SNR and MSE --")
for fs in sampling_rates:
    print(f"\nSampling rate {fs} Hz:")
    resampled_audio = resample_audio(original_audio, base_fs, fs)
    all_files[fs] = []

    for b in quantization_bits:
        filename = f"output_{fs}Hz_{b}bit.wav"
        audio_q = quantize(resampled_audio, b)
        audio_q = np.clip(audio_q, -32767, 32767)
        write(filename, fs, audio_q.astype(np.int16))

        # Match lengths
        min_len = min(len(resampled_audio), len(audio_q))
        snr = calculate_snr(resampled_audio[:min_len], audio_q[:min_len])
        mse = calculate_mse(resampled_audio[:min_len], audio_q[:min_len])

        print(f"{b} bits ; SNR: {snr:.2f} dB ; MSE: {mse:.2f}")
        snr_results.append((fs, b, snr))
        mse_results.append((fs, b, mse))
        all_files[fs].append(filename)

    if fs == base_fs:
        all_files[fs].append("original_base.wav")

# Plots
plot_results(snr_results, "SNR [dB]", "SNR vs Bit Depth and Sampling Rate")
plot_results(mse_results, "MSE", "MSE vs Bit Depth and Sampling Rate")

print("\n-- Part 4 - Playback --")
while True:
    print("\nAvailable sampling rates:")
    for idx, fs in enumerate(sampling_rates):
        print(f"{idx + 1}. {fs} Hz")
    choice = input("Choose sampling rate number (1-4) to play recordings, or type 'q' to quit: ")

    if choice.lower() == 'q':
        print("Playback ended.")
        break
    elif choice in ['1', '2', '3', '4']:
        selected_fs = sampling_rates[int(choice) - 1]
        print(f"\nPlaying recordings for {selected_fs} Hz:")
        for filename in all_files[selected_fs]:
            play_audio(filename)
    else:
        print("Invalid choice. Try again.")

print("\n-- Part 5 - Conclusions --\n"
      "- The best sound quality is achieved at 44100 Hz sampling rate with 16-bit quantization.\n"
      "- SNR increases linearly with the number of bits, regardless of the sampling rate.\n"
      "- MSE is very high at 2-bit quantization, but drops exponentially – from 6 bits onward, the quality is close to original,\n"
      "  and at 8 bits it is nearly indistinguishable.\n"
      "- There is no perceptible difference in audio quality between 8-, 12-, and 16-bit versions (at least to the human ear).\n")
