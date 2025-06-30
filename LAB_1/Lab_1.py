from Crypto.Cipher import AES
import Crypto.Random
import math

def generate_counter_iv(counter):
    iv = counter.to_bytes(16, byteorder='big')
    return iv

def calculate_mic(encrypted_data, key, counter):
    mic = b""
    num_blocks = math.ceil(len(encrypted_data) / 16)

    for i in range(num_blocks):
        counter_iv = generate_counter_iv(counter + i)
        keystream_block = AES.new(key, AES.MODE_ECB).encrypt(counter_iv)
        mic_block = bytearray(16)

        for j in range(16):
            index = i * 16 + j
            if index < len(encrypted_data):
                mic_block[j] = encrypted_data[index] ^ keystream_block[j]
            else:
                break
        mic += mic_block
    return mic

def pad_data(data):
    remaining_bytes = 16 - len(data) % 16
    padding = bytes([remaining_bytes]) * remaining_bytes
    return data + padding

def unpad_data(data):
    padding_length = data[-1]
    return data[:-padding_length]

def encrypt_data_ctr(data, key, counter):
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted_data = b""
    num_blocks = len(data) // 16

    for i in range(num_blocks):
        counter_iv = generate_counter_iv(counter + i)
        keystream_block = cipher.encrypt(counter_iv)
        data_block = data[i * 16: (i + 1) * 16]
        encrypted_block = bytes(data_byte ^ keystream_byte for data_byte, keystream_byte in zip(data_block, keystream_block))
        encrypted_data += encrypted_block

    counter_iv = generate_counter_iv(counter + num_blocks)
    keystream_block = cipher.encrypt(counter_iv)
    remaining_bytes = len(data) % 16
    encrypted_block = bytes(data_byte ^ keystream_byte for data_byte, keystream_byte in zip(data[num_blocks * 16:], keystream_block[:remaining_bytes]))
    encrypted_data += encrypted_block
    return encrypted_data

def simulate_send_receive(encrypted_data, key, counter, original_data_mic):
    received_encrypted_data = encrypted_data
    decrypted_data = encrypt_data_ctr(received_encrypted_data, key, counter)
    unpadded_data = unpad_data(decrypted_data)
    decrypted_data_mic = calculate_mic(unpadded_data, key, counter)

    if original_data_mic != decrypted_data_mic:
        raise Exception("MIC-oт не се совпаѓа!")
    return unpadded_data

def main():
    key = Crypto.Random.get_random_bytes(16)
    counter = 0
    data = input("Внесете ја вашата порака: ").encode()
    encrypted_data = encrypt_data_ctr(pad_data(data), key, counter)
    print("Енкриптирана порака:", encrypted_data)
    original_data_mic = calculate_mic(data, key, counter)
    decrypted_data = simulate_send_receive(encrypted_data, key, counter, original_data_mic)
    print("Декриптирана порака:", decrypted_data.decode())

if __name__ == "__main__":
    main()
