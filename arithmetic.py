#!/usr/bin/env python3
import time
import os
from mpmath import *
import filecmp
from collections import Counter

def arithmetic_encode(source_bytes):
    maximum = 4294967295
    third = 3221225472
    quarter = 1073741824
    half = 2147483648

    bytes_freq = Counter(source_bytes)
    probabilities = {}
    for ch, count in bytes_freq.items():
        probabilities[ch] = count / len(source_bytes)

    cumulative_freq = [0.0]
    for symbol in probabilities.values():
        cumulative_freq.append(cumulative_freq[-1] + symbol)
    cumulative_freq.pop()
    cumulative_freq = {k: v for k, v in zip(probabilities.keys(), cumulative_freq)}

    encoded_numbers = []
    lower_bound, upper_bound = 0, maximum
    straddle = 0

    for byte in source_bytes:
        range_width  = upper_bound  - lower_bound + 1

        lower_bound += ceil(range_width * cumulative_freq[byte])
        upper_bound = lower_bound + floor(range_width * probabilities[byte])

        temporary_numbers = []
        while True:
            if upper_bound < half:
                temporary_numbers.append(0)
                temporary_numbers.extend([1]*straddle)
                straddle = 0
            elif lower_bound >= half:
                temporary_numbers.append(1)
                temporary_numbers.extend([0]*straddle)
                straddle = 0
                lower_bound -= half
                upper_bound -= half
            elif lower_bound >= quarter and upper_bound < third:
                straddle += 1
                lower_bound -= quarter
                upper_bound -= quarter
            else:
                break

            if temporary_numbers:
                encoded_numbers.extend(temporary_numbers)
                temporary_numbers = []

            lower_bound *= 2
            upper_bound = 2 * upper_bound + 1

    encoded_numbers.extend([0] + [1]*straddle if lower_bound < quarter else [1] + [0]*straddle)

    return encoded_numbers

def arithmetic_decode(encoded_numbers, probability_model, text_length):
    prec = 32
    maximum = 4294967295
    third = 3221225472
    quarter = 1073741824
    half = 2147483648

    alphabet = list(probability_model)
    cumulative_freq = [0]
    for symbol_index in probability_model:
        cumulative_freq.append(cumulative_freq[-1] + probability_model[symbol_index])
    cumulative_freq.pop()

    probability_model = list(probability_model.values())

    encoded_numbers.extend(prec * [0])
    decoded_symbols = text_length * [0]

    current_value = int(''.join(str(a) for a in encoded_numbers[0:prec]), 2)
    bit_position = prec
    lower_bound, upper_bound = 0, maximum

    decoded_position = 0
    while 1:
        current_range = upper_bound - lower_bound+1
        symbol_index = len(cumulative_freq)  # установим значение по умолчанию
        value_to_find = (current_value - lower_bound) / current_range
        for i, item in enumerate(cumulative_freq):
            if item >= value_to_find:
                symbol_index = i
                break
        symbol_index -= 1
        decoded_symbols[decoded_position] = alphabet[symbol_index]

        lower_bound = lower_bound + ceil(cumulative_freq[symbol_index] * current_range)
        upper_bound = lower_bound + floor(probability_model[symbol_index] * current_range)

        while True:
            if upper_bound < half:
                pass
            elif lower_bound >= half:
                lower_bound = lower_bound - half
                upper_bound = upper_bound - half
                current_value = current_value - half
            elif lower_bound >= quarter and upper_bound < third:
                lower_bound = lower_bound - quarter
                upper_bound = upper_bound - quarter
                current_value = current_value - quarter
            else:
                break
            lower_bound = 2 * lower_bound
            upper_bound = 2 * upper_bound + 1
            current_value = 2 * current_value + encoded_numbers[bit_position]
            bit_position += 1
            if bit_position == len(encoded_numbers)+1:
                break

        decoded_position += 1
        if decoded_position == text_length or bit_position == len(encoded_numbers) +1:
            break
    return bytes(decoded_symbols)

def encode(file_name):
    with open(file_name, 'rb') as source_file:
        input_bytes = source_file.read()

    byte_freq = dict(Counter(input_bytes))

    encoded_sequence = arithmetic_encode(input_bytes)
    encoded_sequence_str = ''.join(map(str, encoded_sequence))

    padding_bits_count = 8 - len(encoded_sequence_str) % 8
    encoded_sequence_str += "0" * padding_bits_count

    padding_info_str = "{0:08b}".format(padding_bits_count)
    padded_encoded_str = padding_info_str + encoded_sequence_str

    output_byte_array = bytearray([int(padded_encoded_str[i:i + 8], 2) for i in range(0, len(padded_encoded_str), 8)])

    with open('encoded', 'wb') as encoded_file:
        encoded_file.write(len(input_bytes).to_bytes(4, 'little'))
        encoded_file.write((len(byte_freq.keys()) - 1).to_bytes(1, 'little'))

        for byte_value, frequency in byte_freq.items():
            encoded_file.write(byte_value.to_bytes(1, 'little'))
            encoded_file.write(frequency.to_bytes(4, 'little'))

        encoded_file.write(bytes(output_byte_array))

def decode(file_name):
    with open(file_name, 'rb') as encoded_file:
        encoded_data_bytes = encoded_file.read()

    original_file_length = int.from_bytes(encoded_data_bytes[0:4], 'little')
    unique_byte_count = encoded_data_bytes[4] + 1
    header_bytes = encoded_data_bytes[5: 5 * unique_byte_count + 5]

    byte_frequencies = dict()
    for i in range(unique_byte_count):
        byte_value = header_bytes[i * 5]
        frequency = int.from_bytes(header_bytes[i * 5 + 1:i * 5 + 5], 'little')
        byte_frequencies[byte_value] = frequency

    probabilities = {}
    for ch, count in byte_frequencies.items():
        probabilities[ch] = count / original_file_length

    encoded_text_bytes = encoded_data_bytes[5 * (encoded_data_bytes[4] + 1) + 5:]
    padded_encoded_str = ''.join([bin(byte)[2:].rjust(8, '0') for byte in encoded_text_bytes])

    padding_bits_count = int(padded_encoded_str[:8], 2)
    encoded_sequence = padded_encoded_str[8: -padding_bits_count if padding_bits_count != 0 else None]
    encoded_sequence = [int(bit) for bit in encoded_sequence]

    decoded_data = arithmetic_decode(encoded_sequence, probabilities, original_file_length)

    with open('decoded', 'wb') as decoded_file:
        decoded_file.write(decoded_data)

if __name__ == '__main__':
    # Encode
    src = 'source'
    start_time = time.time()
    encode(src)
    end_time = time.time()
    encode_time = end_time - start_time

    original_size = os.path.getsize(src)
    compressed_size = os.path.getsize('encoded')
    compression_ratio = (original_size - compressed_size) / original_size * 100

    print(f"Время кодирования: {encode_time:.4f} сек.")
    print(f"Процент сжатия: {compression_ratio:.2f}%")
    
    # Decode
    enc = 'encoded'
    start_time = time.time()
    decode(enc)
    end_time = time.time()
    decode_time = end_time - start_time
    
    print(f"Время декодирования: {decode_time:.4f} сек.")
    
    if filecmp.cmp('source', 'decoded'):
        print("Исходный файл и декодированный - равны")
    else:
        print("Исходный файл и декодированный - НЕ РАВНЫ!!!")