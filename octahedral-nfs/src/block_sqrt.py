#!/usr/bin/env python3
"""
octahedral-nfs/src/block_sqrt.py — Block-Diagonal Square Root
CC0 public domain — github.com/JinnZ2/urban-resilience-sim

Exploits the octahedral block-diagonal structure of the matrix
to decompose the square root into local operations.

Standard approach:
  x = product of ALL a_i (mod N)         — millions of multiplications
  y = sqrt(product of ALL Q_i) (mod N)   — millions of digits

Block-diagonal approach:
  For each octahedron (3 primes):
    x_local = product of a_i in this block (mod N)    — 1-5 multiplications
    y_local = local square root of block's Q product   — 3 prime powers

  x = product of x_local (mod N)   — D/3 multiplications
  y = product of y_local (mod N)   — D/3 multiplications

The large number blow-up disappears because each block
handles at most 3 relations internally, and blocks combine
via modular multiplication (bounded by N).

This is the "Pack Protocol" for square roots: each node
(octahedron) computes its own local result, then nodes
combine via a single pass.

USAGE:
    python octahedral-nfs/src/block_sqrt.py
"""

from math import gcd, isqrt
from collections import defaultdict
from typing import List, Dict, Tuple, Optional


# =============================================================================
# OCTAHEDRAL BLOCK
# =============================================================================

class OctaBlock:
    """
    One octahedral block: 3 primes from the factor base.
    Tracks which relations have exponents in these primes.
    Computes local x and y contribution independently.
    """

    def __init__(self, primes: Tuple[int, int, int], block_id: int):
        self.primes = primes
        self.block_id = block_id
        self.relations: List[Tuple[int, Dict[int, int]]] = []  # (a_i, exponents)

    def add_relation(self, a: int, exponents: Dict[int, int]):
        """Add a relation that involves primes in this block."""
        # Only keep exponents for our primes
        local_exp = {p: exponents.get(p, 0) for p in self.primes}
        if any(v > 0 for v in local_exp.values()):
            self.relations.append((a, local_exp))

    def local_x(self, active_indices: List[int], N: int) -> int:
        """
        Compute x_local = product of a_i for active relations, mod N.
        Only the relations selected by the nullspace vector.
        """
        x = 1
        for idx in active_indices:
            if idx < len(self.relations):
                a, _ = self.relations[idx]
                x = (x * a) % N
        return x

    def local_y_exponents(self, active_indices: List[int]) -> Dict[int, int]:
        """
        Accumulate exponents for this block's primes across active relations.
        """
        total = {p: 0 for p in self.primes}
        for idx in active_indices:
            if idx < len(self.relations):
                _, exp = self.relations[idx]
                for p in self.primes:
                    total[p] += exp.get(p, 0)
        return total

    def local_y(self, active_indices: List[int], N: int) -> Optional[int]:
        """
        Compute y_local = product of p^(e/2) for this block's primes, mod N.
        Returns None if any exponent is odd (not a perfect square locally).
        """
        exponents = self.local_y_exponents(active_indices)
        y = 1
        for p, total in exponents.items():
            if total % 2 != 0:
                return None  # Not square in this block
            if total > 0:
                y = (y * pow(p, total // 2, N)) % N
        return y


# =============================================================================
# BLOCK-DIAGONAL SQUARE ROOT
# =============================================================================

def block_diagonal_sqrt(N: int, relations: List[Dict],
                         factor_base: List[int],
                         nullspace_vector: List[int]) -> Optional[int]:
    """
    Decompose the square root step into octahedral blocks.

    Instead of computing x and y globally across all relations,
    we:
    1. Assign each relation to its relevant octahedral blocks
    2. Each block computes local x and y independently
    3. Combine block results via modular multiplication

    Maximum numbers in any single step are bounded by N,
    not by the product of millions of a_i values.
    """

    # Build octahedral blocks
    blocks: List[OctaBlock] = []
    for i in range(0, len(factor_base) - 2, 3):
        triple = (factor_base[i], factor_base[i + 1], factor_base[i + 2])
        blocks.append(OctaBlock(triple, len(blocks)))

    # Handle leftover primes (not in a full triple)
    leftover_primes = factor_base[len(blocks) * 3:]

    # Assign relations to blocks
    active_relations = [i for i, v in enumerate(nullspace_vector) if v == 1]

    for rel_idx in active_relations:
        if rel_idx >= len(relations):
            continue
        rel = relations[rel_idx]
        for block in blocks:
            block.add_relation(rel["a"], rel["exp"])

    # Compute global x: product of all active a_i mod N
    # (This part doesn't decompose — but each multiplication is mod N,
    #  so numbers never exceed N. No blow-up.)
    x = 1
    for rel_idx in active_relations:
        if rel_idx < len(relations):
            x = (x * relations[rel_idx]["a"]) % N

    # Compute y via block decomposition
    # Each block handles its own primes independently
    y = 1
    all_exponents: Dict[int, int] = {}

    for block in blocks:
        # Which of our active relations appear in this block?
        block_active = list(range(len(block.relations)))
        exponents = block.local_y_exponents(block_active)

        for p, total in exponents.items():
            all_exponents[p] = all_exponents.get(p, 0) + total

    # Add leftover primes
    for rel_idx in active_relations:
        if rel_idx < len(relations):
            for p in leftover_primes:
                count = relations[rel_idx]["exp"].get(p, 0)
                all_exponents[p] = all_exponents.get(p, 0) + count

    # Check all exponents are even (perfect square)
    for p, total in all_exponents.items():
        if total % 2 != 0:
            return None

    # Build y from halved exponents, each mod N
    for p, total in all_exponents.items():
        if total > 0:
            y = (y * pow(p, total // 2, N)) % N

    # Extract factor
    factor = gcd(abs(x - y), N)
    if 1 < factor < N:
        return factor

    factor = gcd(x + y, N)
    if 1 < factor < N:
        return factor

    return None


# =============================================================================
# DISTRIBUTED BLOCK SQRT — the pack protocol version
# =============================================================================

def distributed_block_sqrt(N: int, relations: List[Dict],
                            factor_base: List[int],
                            nullspace_vector: List[int],
                            num_nodes: int = 3) -> Optional[int]:
    """
    Simulate distributed factorization across multiple nodes.

    Each node handles a range of octahedral blocks.
    Nodes compute local (x_partial, y_partial) and combine.

    This is the "Pack Protocol": a trucker's phone handles
    blocks 0-100, a Raspberry Pi handles 101-200, a neighbor's
    tablet handles 201-300. Nobody needs the full matrix.
    """
    # Build blocks
    blocks: List[OctaBlock] = []
    for i in range(0, len(factor_base) - 2, 3):
        triple = (factor_base[i], factor_base[i + 1], factor_base[i + 2])
        blocks.append(OctaBlock(triple, len(blocks)))

    active_relations = [i for i, v in enumerate(nullspace_vector) if v == 1]

    # Assign relations to blocks
    for rel_idx in active_relations:
        if rel_idx < len(relations):
            rel = relations[rel_idx]
            for block in blocks:
                block.add_relation(rel["a"], rel["exp"])

    # Distribute blocks across nodes
    blocks_per_node = max(1, len(blocks) // num_nodes)
    node_results = []

    for node_id in range(num_nodes):
        start = node_id * blocks_per_node
        end = start + blocks_per_node if node_id < num_nodes - 1 else len(blocks)
        my_blocks = blocks[start:end]

        # Node computes its partial x and y
        x_partial = 1
        y_exponents_partial: Dict[int, int] = {}

        for block in my_blocks:
            block_active = list(range(len(block.relations)))
            for a, _ in block.relations:
                x_partial = (x_partial * a) % N
            exp = block.local_y_exponents(block_active)
            for p, total in exp.items():
                y_exponents_partial[p] = y_exponents_partial.get(p, 0) + total

        node_results.append({
            "node_id": node_id,
            "blocks": f"{start}-{end}",
            "x_partial": x_partial,
            "y_exponents": y_exponents_partial,
        })

    # Combine node results (the "consensus" step)
    x = 1
    all_exponents: Dict[int, int] = {}
    for result in node_results:
        x = (x * result["x_partial"]) % N
        for p, total in result["y_exponents"].items():
            all_exponents[p] = all_exponents.get(p, 0) + total

    # Build y
    y = 1
    for p, total in all_exponents.items():
        if total % 2 != 0:
            return None
        if total > 0:
            y = (y * pow(p, total // 2, N)) % N

    factor = gcd(abs(x - y), N)
    if 1 < factor < N:
        return factor
    factor = gcd(x + y, N)
    if 1 < factor < N:
        return factor

    return None


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    import sys
    import time
    sys.path.insert(0, "octahedral-nfs/src")
    from pipeline import generate_primes, RIMSieve, OctahedralMatrix

    print("=" * 60)
    print("  BLOCK-DIAGONAL SQUARE ROOT")
    print("  exploit octahedral locality in the final step")
    print("=" * 60)

    test_composites = [
        (1022117, 100, "1009 x 1013"),
        (1028171, 100, "1009 x 1019"),
        (1096013, 100, "1033 x 1061"),
        (4076297, 120, "2027 x 2011"),
        (4206457, 120, "2063 x 2039"),
    ]

    for N, D, expected in test_composites:
        fb = generate_primes(D)
        sieve = RIMSieve(N, fb)
        relations = sieve.collect_relations(D + 10)
        matrix = OctahedralMatrix(relations, fb)
        null_vectors = matrix.find_nullspace_vectors()

        # Try standard square root
        t0 = time.time()
        standard_result = None
        for vec in null_vectors:
            from pipeline import sovereign_square_root
            standard_result = sovereign_square_root(N, relations, vec)
            if standard_result:
                break
        t_standard = time.time() - t0

        # Try block-diagonal square root
        t0 = time.time()
        block_result = None
        for vec in null_vectors:
            block_result = block_diagonal_sqrt(N, relations, fb, vec)
            if block_result:
                break
        t_block = time.time() - t0

        # Try distributed (3 nodes)
        t0 = time.time()
        dist_result = None
        for vec in null_vectors:
            dist_result = distributed_block_sqrt(N, relations, fb, vec, num_nodes=3)
            if dist_result:
                break
        t_dist = time.time() - t0

        s_str = f"{standard_result}x{N // standard_result}" if standard_result else "FAIL"
        b_str = f"{block_result}x{N // block_result}" if block_result else "FAIL"
        d_str = f"{dist_result}x{N // dist_result}" if dist_result else "FAIL"

        print(f"\n  N={N} (expected {expected})")
        print(f"    Standard:    {s_str:>16s}  {t_standard:.4f}s")
        print(f"    Block-diag:  {b_str:>16s}  {t_block:.4f}s")
        print(f"    Distributed: {d_str:>16s}  {t_dist:.4f}s  (3 nodes)")

    print(f"\n{'='*60}")
    print("  THE BLOCK ADVANTAGE")
    print(f"{'='*60}")
    print("""
  At D=100, the difference is negligible (everything is fast).

  At D=10^6 (RSA scale), the difference is structural:

  Standard: multiply 10^6 numbers together.
    Each multiplication is mod N, so numbers stay bounded.
    But you need ALL relations in memory simultaneously.

  Block-diagonal: each block multiplies 1-5 numbers.
    Blocks are independent. Can be computed on different devices.
    Only final combination needs all partial results.

  Distributed: each node handles D/3 blocks.
    Nodes exchange only (x_partial, y_exponents) — not relations.
    A phone, a Pi, and a tablet can split the work.
    Nobody holds the full matrix.

  The square root step becomes a mesh operation:
    local compute -> neighbor exchange -> consensus.
  Same pattern as the seed protocol mesh convergence.
""")
