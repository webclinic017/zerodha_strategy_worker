"""
Tree node is used for validation of the expression tree
"""
from collections import deque
from talib import abstract


class ConditionNode:
    def __init__(self, value, node_type, kwargs):
        self.value = value
        self.node_type = node_type
        self.kwargs = kwargs

        self.right_child = None
        self.left_child = None

    def __str__(self):
        return f"({self.value}, {self.node_type})"

    @classmethod
    def from_dict(cls, data: dict):
        if data == None:
            return None

        node = cls(
            value=data["value"],
            node_type=data["node_type"],
            kwargs=data.get("kwargs", {}),
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
            print(node.value)

            return True

        if node.node_type == "operator":
            print(node.value)

            return True

        if node.node_type == "indicator":
            print(node.value)
            print(node.kwargs)

            print(
                abstract.Function(node.value)(
                    historical_data,
                    **node.kwargs.get("inputs", {}),
                    **node.kwargs.get("parameters", {}),
                )
            )

            return True

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
