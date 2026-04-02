"""
Octahedral block decomposition of the exponent matrix.

The key insight: when primes are grouped into octahedra of 3,
the exponent matrix becomes block-diagonal with local coupling.
"""

import numpy as np

def build_parity_matrix(relations, factor_base, prime_to_index):
    """
    Build GF(2) parity matrix from smooth relations.
    
    Returns:
        matrix: list of lists or numpy array
        rows: number of relations
        cols: number of primes
    """
    rows = len(relations)
    cols = len(factor_base)
    
    # Use Python lists for minimal memory
    matrix = [[0] * cols for _ in range(rows)]
    
    for i, rel in enumerate(relations):
        for p, exp in rel['exponents'].items():
            if p in prime_to_index:
                j = prime_to_index[p]
                matrix[i][j] ^= (exp % 2)  # XOR for GF(2)
                
    return matrix


def octahedral_blocks(matrix, n_octahedra):
    """
    Decompose matrix into octahedral blocks (3 columns each).
    
    Returns:
        list of block matrices, each with 3 columns
    """
    blocks = []
    for octa_idx in range(n_octahedra):
        start = octa_idx * 3
        end = start + 3
        
        # Extract columns for this octahedron
        block = []
        for row in matrix:
            block_row = row[start:end]
            if any(block_row):
                block.append(block_row)
                
        if block:
            blocks.append({
                'index': octa_idx,
                'matrix': block,
                'rows': len(block),
                'rank': None  # Will compute
            })
            
    return blocks


def block_rank(block_matrix):
    """
    Compute rank of a 3-column block over GF(2).
    Simple elimination, small enough to be fast.
    """
    if not block_matrix:
        return 0
        
    # Convert to list of rows
    rows = [row[:] for row in block_matrix]
    n_rows = len(rows)
    n_cols = len(rows[0]) if rows else 0
    
    rank = 0
    for col in range(n_cols):
        # Find pivot
        pivot = -1
        for row in range(rank, n_rows):
            if rows[row][col]:
                pivot = row
                break
                
        if pivot == -1:
            continue
            
        # Swap rows
        if pivot != rank:
            rows[rank], rows[pivot] = rows[pivot], rows[rank]
            
        # Eliminate
        for row in range(n_rows):
            if row != rank and rows[row][col]:
                for c in range(n_cols):
                    rows[row][c] ^= rows[rank][c]
                    
        rank += 1
        
    return rank
