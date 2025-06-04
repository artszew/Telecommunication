import heapq  # for selecting least frequent symbols
from collections import Counter
from typing import Dict


class Node:
    def __init__(self, symbol, frequency):
        self.symbol = symbol
        self.frequency = frequency
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.frequency < other.frequency


def get_n_grams(text: str, n: int):
    return [text[i:i + n] for i in range(0, len(text), n)]


def build_frequency_dict(n_grams):
    return Counter(n_grams)  # count symbols


def build_tree(freq_dict):
    heap = [Node(sym, freq) for sym, freq in freq_dict.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        leaf1 = heapq.heappop(heap)
        leaf2 = heapq.heappop(heap)
        merged = Node(None, leaf1.frequency + leaf2.frequency)
        merged.left = leaf1
        merged.right = leaf2
        heapq.heappush(heap, merged)

    return heap[0]  # root


def build_codebook(root: Node) -> Dict[str, str]:
    codebook = {}

    def _build(node, current_code):
        if node is None:
            return
        if node.symbol is not None:
            codebook[node.symbol] = current_code if current_code != "" else "0"
            return
        _build(node.left, current_code + "0")
        _build(node.right, current_code + "1")

    _build(root, "")
    return codebook


def encode(text: str, codebook: Dict[str, str], n: int) -> str:
    n_grams = get_n_grams(text, n)
    return ''.join(codebook[ng] for ng in n_grams)


def decode(encoded_text: str, root: Node) -> str:
    decoded = []
    node = root
    for bit in encoded_text:
        node = node.left if bit == '0' else node.right
        if node.symbol is not None:
            decoded.append(node.symbol)
            node = root
    return ''.join(decoded)
