"""
Implementation of an SMC client.

MODIFY THIS FILE.
"""
# You might want to import more classes if needed.

import collections
import json
from typing import (
    Dict,
    Set,
    Tuple,
    Union
)

from communication import Communication
from expression import (
    Expression,
    Secret,
    AddExpression,
    SubExpression,
    MulExpression,
    Scalar,
)

from protocol import ProtocolSpec
from secret_sharing import(
    reconstruct_secret,
    share_secret,
    Share,
    modulus,
)

# Feel free to add as many imports as you want.


class SMCParty:
    """
    A client that executes an SMC protocol to collectively compute a value of an expression together
    with other clients.

    Attributes:
        client_id: Identifier of this client
        server_host: hostname of the server
        server_port: port of the server
        protocol_spec (ProtocolSpec): Protocol specification
        value_dict (dict): Dictionary assigning values to secrets belonging to this client.
    """

    def __init__(
            self,
            client_id: str,
            server_host: str,
            server_port: int,
            protocol_spec: ProtocolSpec,
            value_dict: Dict[Secret, int]
        ):
        self.comm = Communication(server_host, server_port, client_id)

        self.client_id = client_id
        self.protocol_spec = protocol_spec
        self.value_dict = value_dict
        self.shares_self = {}

    def run(self) -> int:
        """
        The method the client use to do the SMC.
        """
        items = self.value_dict.items()
        # Calculate the shares for your own secrets,...
        for item in items:
            shares = share_secret(item[1], len(self.protocol_spec.participant_ids))
            # ...save your own shares,...
            self.shares_self[str(item[0].id)] = shares[-1]
            i = 0
            # ...and saend the other shares to the other parties
            for participant in self.protocol_spec.participant_ids:
                if participant != self.client_id:
                    self.comm.send_private_message(participant, str(item[0].id), str(shares[i].value))
                    i += 1
        # Compute your local result,...
        intermediate_result = self.process_expression(self.protocol_spec.expr).value
        intermediate_results = [intermediate_result]
        # ...broadcast it,...
        self.comm.publish_message('final', str(intermediate_result))
        for participant in self.protocol_spec.participant_ids:
            if participant != self.client_id:
                intermediate_results.append(int(self.comm.retrieve_public_message(participant, 'final')))
        # ...and add all other local results
        result = 0
        for share in intermediate_results:
            result += share

        return result % modulus

    def process_expression(
            self,
            expr: Expression
        ):
        """ AddExpression """
        if isinstance(expr, AddExpression):
            # Checking if we are the first party to see if we have to add a constant or not
            if self.client_id != self.protocol_spec.participant_ids[0]:

                # Checking if we are adding constants or secrets to determine if term has to be added or not
                # constant + ...
                if isinstance(expr.left, Scalar):
                    # ...secret => secret
                    if isinstance(expr.right, Secret):
                        return self.process_expression(expr.right)
                    # ...constant => sum
                    elif isinstance(expr.right, Scalar):
                        return self.process_expression(expr.left) + self.process_expression(expr.right)
                    # Check if expression is constant (e.g. constant + constant) or not (e.g. constant + secret)
                    elif isinstance(expr.right, AddExpression) or isinstance(expr.right, SubExpression) or isinstance(expr.right, MulExpression):
                        right_hand_side = self.process_expression(expr.right)
                        # ...constant => sum
                        if right_hand_side.constant:
                            return self.process_expression(expr.left) + right_hand_side
                        # ...no constant => rhs
                        else:
                            return right_hand_side
                # secret + ...
                elif isinstance(expr.left, Secret):
                    # ...secret => sum
                    if isinstance(expr.right, Secret):
                        return self.process_expression(expr.left) + self.process_expression(expr.right)
                    # ...constant => secret
                    elif isinstance(expr.right, Scalar):
                        return self.process_expression(expr.left)
                    # Check if expression is constant (e.g. constant + constant) or not (e.g. constant + secret)
                    elif isinstance(expr.right, AddExpression) or isinstance(expr.right, SubExpression) or isinstance(expr.right, MulExpression):
                        right_hand_side = self.process_expression(expr.right)
                        # ...constant => secret
                        if right_hand_side.constant:
                            return self.process_expression(expr.left)
                        # ...no constant => sum
                        else:
                            return self.process_expression(expr.left) + right_hand_side

                elif isinstance(expr.left, AddExpression) or isinstance(expr.left, SubExpression) or isinstance(expr.left, MulExpression):
                    left_hand_side = self.process_expression(expr.left)
                    # constant + ...
                    if left_hand_side.constant:
                        # ... secret => secret
                        if isinstance(expr.right, Secret):
                            return self.process_expression(expr.right)
                        # ... constant => sum
                        elif isinstance(expr.right, Scalar):
                            return left_hand_side + self.process_expression(expr.right)
                        elif isinstance(expr.right, AddExpression) or isinstance(expr.right,SubExpression) or isinstance(expr.right, MulExpression):
                            right_hand_side = self.process_expression(expr.right)
                            # ...constant => sum
                            if right_hand_side.constant:
                                return left_hand_side + right_hand_side
                            # ... no constant => rhs
                            else:
                                return right_hand_side
                    # no constant + ...
                    else:
                        # secret => sum
                        if isinstance(expr.right, Secret):
                            return left_hand_side + self.process_expression(expr.right)
                        # ... constant => lhs
                        elif isinstance(expr.right, Scalar):
                            return  left_hand_side
                        elif isinstance(expr.right, AddExpression) or isinstance(expr.right,SubExpression) or isinstance(expr.right, MulExpression):
                            right_hand_side = self.process_expression(expr.right)
                            # ...constant => lhs
                            if right_hand_side.constant:
                                return left_hand_side
                            # ...no constant => sum
                            else:
                                return left_hand_side + right_hand_side

            # We are the first party, add constant regardless of the expression
            return self.process_expression(expr.left) + self.process_expression(expr.right)

        """ SubExpression """
        if isinstance(expr, SubExpression):
            # Checking if we are the first party to see if we have to subtract a constant or not
            if self.client_id != self.protocol_spec.participant_ids[0]:

                # Checking if we are adding constants or secrets to determine if term has to be added or not
                # constant - ...
                if isinstance(expr.left, Scalar):
                    # ...secret => secret
                    if isinstance(expr.right, Secret):
                        return self.process_expression(expr.right)
                    # ...constant => sum
                    elif isinstance(expr.right, Scalar):
                        return self.process_expression(expr.left) - self.process_expression(expr.right)
                    # Check if expression is constant (e.g. constant + constant) or not (e.g. constant + secret)
                    elif isinstance(expr.right, AddExpression) or isinstance(expr.right, SubExpression) or isinstance(expr.right, MulExpression):
                        right_hand_side = self.process_expression(expr.right)
                        # ...constant => sum
                        if right_hand_side.constant:
                            return self.process_expression(expr.left) - right_hand_side
                        # ...no constant => rhs
                        else:
                            return right_hand_side
                # secret - ...
                elif isinstance(expr.left, Secret):
                    # ...secret => sum
                    if isinstance(expr.right, Secret):
                        return self.process_expression(expr.left) - self.process_expression(expr.right)
                    # ...constant => secret
                    elif isinstance(expr.right, Scalar):
                        return self.process_expression(expr.left)
                    # Check if expression is constant (e.g. constant + constant) or not (e.g. constant + secret)
                    elif isinstance(expr.right, AddExpression) or isinstance(expr.right, SubExpression) or isinstance(expr.right, MulExpression):
                        right_hand_side = self.process_expression(expr.right)
                        # ...constant => secret
                        if right_hand_side.constant:
                            return self.process_expression(expr.left)
                        # ...no constant => sum
                        else:
                            return self.process_expression(expr.left) - right_hand_side

                elif isinstance(expr.left, AddExpression) or isinstance(expr.left, SubExpression) or isinstance(expr.left, MulExpression):
                    left_hand_side = self.process_expression(expr.left)
                    # constant - ...
                    if left_hand_side.constant:
                        # ... secret => secret
                        if isinstance(expr.right, Secret):
                            return self.process_expression(expr.right)
                        # ... constant => sum
                        elif isinstance(expr.right, Scalar):
                            return left_hand_side - self.process_expression(expr.right)
                        elif isinstance(expr.right, AddExpression) or isinstance(expr.right, SubExpression) or isinstance(expr.right, MulExpression):
                            right_hand_side = self.process_expression(expr.right)
                            # ...constant => sum
                            if right_hand_side.constant:
                                return left_hand_side - right_hand_side
                            # ... no constant => rhs
                            else:
                                return right_hand_side
                    # no constant - ...
                    else:
                        # secret => sum
                        if isinstance(expr.right, Secret):
                            return left_hand_side - self.process_expression(expr.right)
                        # ... constant => lhs
                        elif isinstance(expr.right, Scalar):
                            return left_hand_side
                        elif isinstance(expr.right, AddExpression) or isinstance(expr.right, SubExpression) or isinstance(expr.right, MulExpression):
                            right_hand_side = self.process_expression(expr.right)
                            # ...constant => lhs
                            if right_hand_side.constant:
                                return left_hand_side
                            # ...no constant => sum
                            else:
                                return left_hand_side - right_hand_side

            # We are the first party, subtract constant regardless of the expression
            return self.process_expression(expr.left) - self.process_expression(expr.right)

        """ MulExpression """
        if isinstance(expr, MulExpression):
            # Checking if we need to use beaver multiplication or not
            if isinstance(expr.left, Secret):
                if isinstance(expr.right, Secret):
                    # secret * secret => beaver
                    return self.beaver(self.process_expression(expr.left), self.process_expression(expr.right), expr)
                elif isinstance(expr.right, AddExpression) or isinstance(expr.right, SubExpression) or isinstance(expr.right, MulExpression):
                    right_hand_side = self.process_expression(expr.right)
                    if not right_hand_side.constant:
                        # secret * non constant => beaver
                        return self.beaver(self.process_expression(expr.left), right_hand_side, expr)


            elif isinstance(expr.left, AddExpression) or isinstance(expr.left, SubExpression) or isinstance(expr.left, MulExpression):
                left_hand_side = self.process_expression(expr.left)
                if not left_hand_side.constant:
                    if isinstance(expr.right, Secret):
                        # non constant * secret => beaver
                        return self.beaver(left_hand_side, self.process_expression(expr.right), expr)
                    elif isinstance(expr.right, AddExpression) or isinstance(expr.right, SubExpression) or isinstance(expr.right, MulExpression):
                        right_hand_side = self.process_expression(expr.right)
                        if not right_hand_side.constant:
                            # non constant * non constant => beaver
                            return self.beaver(left_hand_side, right_hand_side, expr)

            # default return (e.g. constant * secret, non constant * constant)
            return self.process_expression(expr.left) * self.process_expression(expr.right)

        """ Secret """
        if isinstance(expr, Secret):
            if str(expr.id) in self.shares_self:
                return self.shares_self[str(expr.id)]
            return Share(int(self.comm.retrieve_private_message(str(expr.id))))

        """ Scalar """
        if isinstance(expr, Scalar):
            return Share(expr.value, True)

        pass

    def beaver(self, left: Share, right: Share, expr):
        """ The algorithm implementing multiplication with beaver triples """
        a, b, c = self.comm.retrieve_beaver_triplet_shares(str(expr.id))
        d = (left.value - a.value) % modulus
        e = (right.value - b.value) % modulus
        self.comm.publish_message(f'{expr.id} d', str(d))
        self.comm.publish_message(f'{expr.id} e', str(e))

        for participant in self.protocol_spec.participant_ids:
            if participant != self.client_id:
                d += int(self.comm.retrieve_public_message(participant, f'{expr.id} d')) % modulus
                e += int(self.comm.retrieve_public_message(participant, f'{expr.id} e')) % modulus

        if self.client_id != self.protocol_spec.participant_ids[0]:
            return Share((d * right.value + e * left.value + c.value) % modulus)
        return Share((d * right.value + e * left.value + c.value - d * e) % modulus)

    # Feel free to add as many methods as you want.
