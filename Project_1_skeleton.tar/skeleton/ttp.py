"""
Trusted parameters generator.

MODIFY THIS FILE.
"""

import collections
import random
from typing import (
    Dict,
    Set,
    Tuple,
)

from communication import Communication
from secret_sharing import (
    share_secret,
    Share,
    modulus,
)


# Feel free to add as many imports as you want.


class TrustedParamGenerator:
    """
    A trusted third party that generates random values for the Beaver triplet multiplication scheme.
    """

    def __init__(self):
        self.participant_ids: Set[str] = set()
        self.beaver_dict: Dict[str, Tuple[Share, Share, Share]] = dict()
        self.operation_dict: Dict[str, Dict] = dict()

    def add_participant(self, participant_id: str) -> None:
        """
        Add a participant.
        """
        self.participant_ids.add(participant_id)

    def retrieve_share(self, client_id: str, op_id: str) -> Tuple[Share, Share, Share]:
        """
        Retrieve a triplet of shares for a given client_id.
        """
        if client_id not in self.participant_ids:
            raise ValueError("Client is not registered as a participant")
        # If we don't have a triplet for the current operation, then generate one, else...
        if op_id not in self.operation_dict.keys():
            number_of_participants = len(self.participant_ids)

            a = random.randint(0, modulus-1)
            share_a = share_secret(a, number_of_participants)

            b = random.randint(0, modulus-1)
            share_b = share_secret(b, number_of_participants)

            c = (a * b) % modulus
            share_c = share_secret(c, number_of_participants)

            beaver_dict = {}
            n = 0
            for m in self.participant_ids:
                beaver_dict[m] = (share_a[n], share_b[n], share_c[n])
                n += 1

            self.operation_dict[op_id] = beaver_dict
            return self.operation_dict[op_id][client_id]
        # ... use the existing triplet
        else:
            return self.operation_dict[op_id][client_id]


    # Feel free to add as many methods as you want.
