from string import ascii_lowercase
import random
def gen_random_uuid():
    alphabet = ascii_lowercase[:6] + "0123456789"
    template = "29f28e1c-f230-486a-a860-f5a784ab9172"
    uuid = []
    for t in template:
        if t != "-":
            uuid.append(random.choice(alphabet))
        else:
            uuid.append(t)
    return "".join(uuid)

if __name__ == "__main__":
    print(gen_random_uuid())


def tmsi_to_hex(tmsi: int)->str:
    """Convert the tmsi as a negative integer to its two's complement representation
        Used to convert UERANSIM tmsi to open5gs TMSI
    """
    twos_comp = (1 << 32) + tmsi

    # Convert the two's complement representation to a hexadecimal string
    hex_str = hex(twos_comp)[2:]

    # Make sure the hexadecimal string has 8 digits (32 bits)
    hex_str = hex_str.zfill(8)

    return hex_str