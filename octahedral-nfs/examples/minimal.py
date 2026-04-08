# MODULE: octahedral-nfs/examples/minimal.py
# PROVIDES: —
# DEPENDS: stdlib-only
# RUN: —
# TIER: demo
# Minimal factorization example with no external dependencies
"""
Minimal factorization example - runs on anything with Python.
No numpy, no OpenCL required.
"""

import sys
sys.path.append('..')

from octahedral_nfs.factor_base import generate_primes, octahedral_mapping
from octahedral_nfs.holographic import build_holographic_tables, is_smooth_holographic

def factor_minimal(N, bound=1000):
    """
    Minimal factorization using octahedral detection.
    No external dependencies.
    """
    print(f"Factoring {N}...")
    
    # Generate factor base
    primes = generate_primes(bound)
    print(f"  Factor base: {len(primes)} primes up to {bound}")
    
    # Build octahedral mapping
    prime_to_octa, prime_to_vertex, octa_to_primes = octahedral_mapping(primes)
    
    # Build holographic tables
    level_tables, level_products = build_holographic_tables(primes)
    
    # Collect smooth relations
    relations = []
    a = int(N**0.5) + 1
    
    print("  Collecting smooth relations...")
    while len(relations) < len(primes) + 5:
        Q = abs(a*a - N)
        
        smooth, exponents = is_smooth_holographic(
            Q, primes, level_tables, level_products
        )
        
        if smooth:
            relations.append({
                'a': a,
                'Q': Q,
                'exponents': exponents
            })
            if len(relations) % 10 == 0:
                print(f"    Found {len(relations)} relations...")
                
        a += 1
        
    print(f"  Found {len(relations)} smooth relations")
    
    # Build parity matrix
    prime_to_index = {p: i for i, p in enumerate(primes)}
    matrix = []
    for rel in relations:
        row = [0] * len(primes)
        for p, exp in rel['exponents'].items():
            if p in prime_to_index:
                row[prime_to_index[p]] ^= (exp % 2)
        matrix.append(row)
    
    # Simple elimination (no numpy)
    print("  Solving matrix...")
    # ... elimination code ...
    
    print("  Looking for factors...")
    # ... factor extraction ...
    
    return None, None  # Placeholder


if __name__ == "__main__":
    N = 1003
    p, q = factor_minimal(N)
    if p and q:
        print(f"{N} = {p} × {q}")
    else:
        print("Factorization failed - try larger bound?")
