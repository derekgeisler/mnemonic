import hashlib
import hmac
import os
import time
from typing import List

# Example wordlist (could be expanded or customized)
wordlist = [
    "apple", "banana", "cherry", "date", "elderberry", "fig", "grape",
    "honeydew", "kiwi", "lemon", "mango", "nectarine", "orange", "papaya"
]

def generate_mnemonic(word_count: int = 12, custom_wordlist: List[str] = None) -> str:
    """Generate a mnemonic from a given wordlist."""
    if custom_wordlist:
        wordlist = custom_wordlist
    entropy = os.urandom(word_count // 3)
    binary_entropy = bin(int.from_bytes(entropy, 'big'))[2:].zfill(word_count * 11)
    mnemonic = []
    for i in range(0, len(binary_entropy), 11):
        index = int(binary_entropy[i:i + 11], 2)
        mnemonic.append(wordlist[index % len(wordlist)])
    return ' '.join(mnemonic)

def mnemonic_to_seed(mnemonic: str, passphrase: str = "") -> bytes:
    """Convert a mnemonic to a seed, with an optional passphrase."""
    return hashlib.pbkdf2_hmac('sha512', mnemonic.encode('utf-8'), ("mnemonic" + passphrase).encode('utf-8'), 2048)

def derive_key(seed: bytes, path: str, secondary_factor: str = "") -> bytes:
    """Derive a key using a path, seed, and optional secondary factor."""
    segments = path.split('/')
    for segment in segments:
        if segment.isdigit():
            seed = hmac.new(seed, int(segment).to_bytes(4, 'big'), hashlib.sha512).digest()
    if secondary_factor:
        seed = hmac.new(seed, secondary_factor.encode('utf-8'), hashlib.sha512).digest()
    return seed[:32]

def time_based_derivation(seed: bytes, time_factor: int = int(time.time())) -> bytes:
    """Derive a key based on the current time as an additional factor."""
    time_bytes = time_factor.to_bytes(8, 'big')
    return hmac.new(seed, time_bytes, hashlib.sha512).digest()[:32]

# Example usage
custom_wordlist = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta", "iota", "kappa", "lambda", "mu"]
mnemonic = generate_mnemonic(12, custom_wordlist)
print("Mnemonic:", mnemonic)

seed = mnemonic_to_seed(mnemonic, passphrase="mysecret")
print("Seed:", seed.hex())

# Derive a key with a custom path and a secondary factor
derived_key = derive_key(seed, path="m/44'/0'/0'/0", secondary_factor="extra_security")
print("Derived Key:", derived_key.hex())

# Derive a key using time-based derivation
time_based_key = time_based_derivation(seed)
print("Time-Based Derived Key:", time_based_key.hex())
