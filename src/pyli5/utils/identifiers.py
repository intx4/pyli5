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