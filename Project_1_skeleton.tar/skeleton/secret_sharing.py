"""
Secret sharing scheme.
"""

from __future__ import annotations

import random
from typing import List

modulus = 181081


class Share:
    """
    A secret share in a finite field.
    """

    def __init__(self, value: int = 0, constant: bool = False, *args, **kwargs):
        # Adapt constructor arguments as you wish
        self.value = value
        self.constant = constant

    def __repr__(self):
        # Helps with debugging.
        return f"{self.__class__.__name__}({self.value})"

    def __add__(self, other):
        return Share((self.value + other.value) % modulus, self.constant and other.constant)

    def __sub__(self, other):
        return Share((self.value - other.value) % modulus, self.constant and other.constant)

    def __mul__(self, other):
        return Share((self.value * other.value) % modulus, self.constant and other.constant)

    def serialize(self):
        """Generate a representation suitable for passing in a message."""
        return str(self.value)

    @staticmethod
    def deserialize(serialized) -> Share:
        """Restore object from its serialized representation."""
        return Share(int(serialized))


def share_secret(secret: int, num_shares: int) -> List[Share]:
    """Generate secret shares."""
    end_share = secret
    shares = []
    for i in range(num_shares - 1):
        share = random.randint(0, modulus-1)
        shares.append(Share(share))
        end_share = (end_share - share) % modulus
    ''' compute last share as the difference b/w the secret and the sum of the other shares '''
    shares_sum = 0
    for s in shares:
        shares_sum += s.value
    shares.append(Share((secret - shares_sum) % modulus))
    return shares


def reconstruct_secret(shares: List[Share]) -> int:
    """Reconstruct the secret from shares."""
    secret = 0
    for s in shares:
        secret = (secret + s.value) % modulus
    return secret

# Feel free to add as many methods as you want.
