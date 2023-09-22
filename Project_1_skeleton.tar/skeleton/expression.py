"""
Tools for building arithmetic expressions to execute with SMC.

Example expression:
>>> alice_secret = Secret()
>>> bob_secret = Secret()
>>> expr = alice_secret * bob_secret * Scalar(2)

MODIFY THIS FILE.
"""

import base64
import random
from typing import Optional

ID_BYTES = 4


def gen_id() -> bytes:
    id_bytes = bytearray(
        random.getrandbits(8) for _ in range(ID_BYTES)
    )
    return base64.b64encode(id_bytes)


class Expression:
    """
    Base class for an arithmetic expression.
    """

    def __init__(
            self,
            id: Optional[bytes] = None
    ):
        # If ID is not given, then generate one.
        if id is None:
            id = gen_id()
        self.id = id

    def __add__(self, other):
        if isinstance(other, Expression):
            return AddExpression(self, other)
        elif isinstance(other, int):
            return AddExpression(self, Scalar(other))
        else:
            raise NotImplementedError("You need to implement this method.")

    def __sub__(self, other):
        if isinstance(other, Expression):
            return SubExpression(self, other)
        elif isinstance(other, int):
            return SubExpression(self, Scalar(other))
        else:
            raise NotImplementedError("You need to implement this method.")

    def __mul__(self, other):
        if isinstance(other, Expression):
            return MulExpression(self, other)
        elif isinstance(other, int):
            return MulExpression(self, Scalar(other))
        else:
            raise NotImplementedError("You need to implement this method.")

    def __hash__(self):
        return hash(self.id)

    # Feel free to add as many methods as you like.


class Scalar(Expression):
    """Term representing a scalar finite field value."""

    def __init__(
            self,
            value: int,
            id: Optional[bytes] = None
    ):
        self.value = value
        super().__init__(id)

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.value)})"

    def __hash__(self):
        return

    # Feel free to add as many methods as you like.


class Secret(Expression):
    """Term representing a secret finite field value (variable)."""

    def __init__(
            self,
            value: Optional[int] = None,
            id: Optional[bytes] = None
    ):
        self.value = value
        super().__init__(id)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self.value if self.value is not None else ''})"
        )

    # Feel free to add as many methods as you like.


# Feel free to add as many classes as you like.
class AddExpression(Expression):
    """Expression representing the addition of two expressions."""

    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right
        super().__init__()

    def __repr__(self):
        # addition, add expr left, right scalar => brackets for expr
        if isinstance(self.left, AddExpression) and isinstance(self.right, Scalar):
            return f"({self.left}) + {self.right}"

        # addition, secret left, scalar right => brackets
        if isinstance(self.left, Secret) and isinstance(self.right, Scalar):
            return f"({self.left} + {self.right})"

        # addition, scalar left, mul expr right => brackets
        if isinstance(self.left, Scalar) and isinstance(self.right, MulExpression):
            return f"({self.left} + {self.right})"

        # addition, add expr left, mul expr right => brackets
        if isinstance(self.left, AddExpression) and isinstance(self.right, MulExpression):
            return f"({self.left} + {self.right})"

        # addition, mul expr left, scalar right => brackets
        if isinstance(self.left, MulExpression) and isinstance(self.right, Scalar):
            return f"({self.left} + {self.right})"

        # addition, add expr left, sub expr right => brackets
        if isinstance(self.left, AddExpression) and isinstance(self.right, SubExpression):
            return f"({self.left} + {self.right})"

        return f"{self.left} + {self.right}"


class SubExpression(Expression):
    """Expression representing the subtraction of two expressions."""

    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right
        super().__init__()

    def __repr__(self):
        # subtraction, add expr left, right secret => brackets
        if isinstance(self.left, AddExpression) and isinstance(self.right, Secret):
            return f"({self.left} - {self.right})"

        return f"{self.left} - {self.right}"


class MulExpression(Expression):
    """Expression representing the multiplication of two expressions."""

    def __init__(self, left: Expression, right: Expression):
        self.left = left
        self.right = right
        super().__init__()

    def __repr__(self):
        # multiplication, add expr left, right scalar => brackets for expr
        if isinstance(self.left, AddExpression) and isinstance(self.right, Scalar):
            return f"({self.left}) * {self.right}"

        # multiplication, secret, scalar = > bracket
        if isinstance(self.left, Secret) and isinstance(self.right, Scalar):
            return f"({self.left} * {self.right})"

        # multiplication, two secret => brackets
        if isinstance(self.left, Secret) and isinstance(self.right, Secret):
            return f"({self.left} * {self.right})"

        # multiplication, sub left expr, add right expr => brackets
        if isinstance(self.left, SubExpression) and isinstance(self.right, AddExpression):
            return f"({self.left} * ({self.right}))"

        # multiplication, add expr left, right secret => brackets for expr
        if isinstance(self.left, AddExpression) and isinstance(self.right, Secret):
            return f"({self.left}) * {self.right}"

        # multiplication, add expr left, add expr right => brackets for expr
        if isinstance(self.left, AddExpression) and isinstance(self.right, AddExpression):
            return f"({self.left} * ({self.right}))"

        return f"{self.left} * {self.right}"
