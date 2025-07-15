import string
import random

def generate_password(length=16):
    characters = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    return ''.join(random.SystemRandom().choice(characters) for _ in range(length))
