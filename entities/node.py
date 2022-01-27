"""
Tree node is used for validation of the expression tree
"""
from collections import deque
from talib import abstract
import operator


class ConditionNode:
    operator_map = {
        ">": operator.gt,
        "<": operator.lt,
        "==": operator.eq,
        ">=": operator.ge,
        "<=": operator.le,
        "!=": operator.ne,
        "and": operator.and_,
        "or": operator.or_,
    }

    def __init__(self, value, node_type, kwargs):
        self.value = value
        self.node_type = node_type
        self.kwargs = kwargs

        self.right_child = None
        self.left_child = None

    def __str__(self):
        if "output" in self.kwargs:
            return f"({self.value}, {self.node_type}, {self.kwargs['output']})"

        return f"({self.value}, {self.node_type})"

    @classmethod
    def from_dict(cls, data: dict):
        if data == None:
            return None

        kwargs = data.get("kwargs", {})

        if kwargs != {}:
            if "parameters" in kwargs:
                for k, v in kwargs["parameters"].items():
                    if k in ["nbdevup", "nbdevdn", "nbdev"]:
                        kwargs["parameters"][k] = float(v)

        node = cls(
            value=data["value"],
            node_type=data["node_type"],
            kwargs=kwargs,
        )

        if "left_child" in data:
            node.left_child = cls.from_dict(data["left_child"])

        if "right_child" in data:
            node.right_child = cls.from_dict(data["right_child"])

        return node

    def evaluate_helper(self, node, historical_data, live_data):
        print(f"[*] evaluate: {node}")

        if node == None:
            return True

        if node.node_type == "constant":
            return float(node.value)

        if node.node_type == "indicator":
            techenical = abstract.Function(node.value)(
                historical_data,
                **node.kwargs.get("inputs", {}),
                **node.kwargs.get("parameters", {}),
            )

            if node.kwargs["output"] in ["real", "integer"]:
                return techenical.tail(1).values[0]
            else:
                return techenical.tail(1)[node.kwargs["output"]].values[0]

        if node.node_type == "operator":
            return self.operator_map[node.value](
                self.evaluate_helper(node.left_child, historical_data, live_data),
                self.evaluate_helper(node.right_child, historical_data, live_data),
            )

        return False

    def evaluate(self, historical_data, live_data):
        return self.evaluate_helper(self, historical_data, live_data)

    @classmethod
    def is_complete_binary_tree(cls, root):
        if root == None:
            return True

        if root.left_child == None and root.right_child == None:
            return True
        elif root.left_child != None and root.right_child != None:
            return cls.is_complete_binary_tree(
                root.left_child
            ) and cls.is_complete_binary_tree(root.right_child)

        return False
