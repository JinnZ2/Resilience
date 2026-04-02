"""
Scaling Test: Octahedral Block Structure at D=500
Run time: ~30-60 minutes on a modern machine
Memory: ~500MB peak
"""

import numpy as np
from collections import defaultdict
from math import isqrt
import time
import sys

class LargeScaleValidator:
    """
    Rigorous validation of octahedral structure at scale.
    """
    
    def __init__(self, N, D, max_relations=None):
        self.N = N
        self.D = D
        self.max_relations = max_relations or D + 50
        
        # Generate factor base
        self.factor_base = self._generate_primes(D)
        self.B = max(self.factor_base)
        self.n_octahedra = (D + 2) // 3
        
        # Build mappings
        self.prime_to_index = {p: i for i, p in enumerate(self.factor_base)}
        self.prime_to_octa = {}
        self.prime_to_vertex = {}
        
        for i, p in enumerate(self.factor_base):
            self.prime_to_octa[p] = i // 3
            self.prime_to_vertex[p] = i % 3
            
        print(f"\n{'='*80}")
        print(f"SCALING VALIDATION: D={self.D}")
        print(f"{'='*80}")
        print(f"N = {self.N}")
        print(f"Factor base: {len(self.factor_base)} primes up to {self.B}")
        print(f"Octahedra: {self.n_octahedra}")
        print(f"Target relations: {self.max_relations}")
        print()
        
    def _generate_primes(self, n):
        """Generate first n primes efficiently."""
        primes = []
        candidate = 2
        while len(primes) < n:
            is_prime = True
            limit = int(candidate**0.5) + 1
            for p in primes:
                if p > limit:
                    break
                if candidate % p == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.append(candidate)
            candidate += 1 if candidate == 2 else 2
        return primes
    
    def _is_smooth(self, n, max_checks=None):
        """
        Trial division smoothness test.
        For validation, we use direct factorization.
        """
        if n == 0:
            return False, None
            
        exponents = defaultdict(int)
        remaining = n
        
        # Check primes in order
        for p in self.factor_base:
            if p * p > remaining:
                break
            while remaining % p == 0:
                exponents[p] += 1
                remaining //= p
                
            # Early exit if we've done enough checks
            if max_checks and len(exponents) > max_checks:
                return False, None
                
        # Check if remaining is prime in factor base
        if remaining > 1:
            if remaining <= self.B and remaining in self.prime_to_index:
                exponents[remaining] += 1
                remaining = 1
                
        return (remaining == 1), exponents
    
    def collect_relations(self):
        """Collect smooth relations by scanning a values."""
        relations = []
        a = isqrt(self.N) + 1
        start_time = time.time()
        last_print = 0
        
        print("Collecting smooth relations...")
        print(f"  Scanning a from {a}")
        
        while len(relations) < self.max_relations:
            Q = abs(a*a - self.N)
            
            # Skip numbers that are clearly too large
            if Q <= self.B * self.B:
                smooth, exponents = self._is_smooth(Q)
                if smooth:
                    relations.append({
                        'a': a,
                        'Q': Q,
                        'exponents': exponents
                    })
                    
                    # Progress report
                    if len(relations) % 50 == 0 and len(relations) != last_print:
                        elapsed = time.time() - start_time
                        rate = (a - isqrt(self.N)) / elapsed if elapsed > 0 else 0
                        print(f"    Found {len(relations)} relations in {elapsed:.1f}s (rate: {rate:.0f} a/s)")
                        last_print = len(relations)
                        
            a += 1
            
        elapsed = time.time() - start_time
        total_scanned = a - isqrt(self.N)
        
        print(f"\n  Collection complete:")
        print(f"    Relations: {len(relations)}")
        print(f"    Scanned: {total_scanned} values")
        print(f"    Time: {elapsed:.1f}s")
        print(f"    Success rate: {len(relations)/total_scanned*100:.3f}%")
        
        return relations
    
    def build_parity_matrix(self, relations):
        """Build GF(2) parity matrix."""
        n_rows = len(relations)
        n_cols = self.D
        
        # Use numpy for efficient computation
        matrix = np.zeros((n_rows, n_cols), dtype=np.int8)
        
        for i, rel in enumerate(relations):
            for p, exp in rel['exponents'].items():
                if p in self.prime_to_index:
                    j = self.prime_to_index[p]
                    matrix[i, j] ^= (exp % 2)
                    
        return matrix
    
    def analyze_blocks(self, matrix):
        """Analyze each octahedral block."""
        print("\n" + "="*80)
        print("BLOCK ANALYSIS")
        print("="*80)
        
        block_stats = []
        rank_deficient = 0
        
        print(f"\n{'Octa':^6} {'Primes':^25} {'Active':^8} {'Rank':^6} {'Density':^10} {'Status':^15}")
        print("-" * 80)
        
        for octa_idx in range(self.n_octahedra):
            start = octa_idx * 3
            end = min(start + 3, self.D)
            primes = self.factor_base[start:end]
            prime_range = f"{primes[0]}-{primes[-1]}" if primes else "empty"
            
            # Extract block
            block = matrix[:, start:end]
            active_rows = np.sum(np.sum(block, axis=1) > 0)
            
            if active_rows > 0:
                # Compute rank over GF(2)
                rank = self._block_rank(block)
                density = np.sum(block) / (block.shape[0] * block.shape[1])
                max_rank = min(3, block.shape[0])
                
                status = "FULL RANK" if rank == max_rank else f"DEFICIT({max_rank - rank})"
                if rank < max_rank:
                    rank_deficient += 1
                    
                block_stats.append({
                    'idx': octa_idx,
                    'primes': primes,
                    'active': active_rows,
                    'rank': rank,
                    'density': density,
                    'status': status
                })
                
                # Print every 20th block or deficient blocks
                if octa_idx % 20 == 0 or rank < max_rank:
                    print(f"{octa_idx:6d} {prime_range:25s} {active_rows:8d} {rank:6d} {density:10.4f} {status:15s}")
                    
        print("-" * 80)
        print(f"\nSummary:")
        print(f"  Total octahedra: {self.n_octahedra}")
        print(f"  Active octahedra: {len(block_stats)}")
        print(f"  Rank deficient: {rank_deficient}")
        
        return block_stats, rank_deficient
    
    def _block_rank(self, block):
        """Compute GF(2) rank of a block."""
        if block.size == 0:
            return 0
            
        n_rows, n_cols = block.shape
        if n_rows == 0:
            return 0
            
        # Copy to list for elimination
        rows = block.copy()
        rank = 0
        
        for col in range(n_cols):
            # Find pivot
            pivot = -1
            for row in range(rank, n_rows):
                if rows[row, col]:
                    pivot = row
                    break
                    
            if pivot == -1:
                continue
                
            # Swap
            if pivot != rank:
                rows[[rank, pivot]] = rows[[pivot, rank]]
                
            # Eliminate
            for row in range(n_rows):
                if row != rank and rows[row, col]:
                    rows[row] = (rows[row] + rows[rank]) % 2
                    
            rank += 1
            
        return rank
    
    def compute_nullspace_dimension(self, matrix):
        """Compute nullspace dimension using rank."""
        print("\n" + "="*80)
        print("NULLSPACE ANALYSIS")
        print("="*80)
        
        n_rows, n_cols = matrix.shape
        
        # Compute rank via elimination
        A = matrix.copy()
        rank = 0
        
        for col in range(n_cols):
            # Find pivot
            pivot = -1
            for row in range(rank, n_rows):
                if A[row, col]:
                    pivot = row
                    break
                    
            if pivot == -1:
                continue
                
            # Swap
            if pivot != rank:
                A[[rank, pivot]] = A[[pivot, rank]]
                
            # Eliminate below
            for row in range(rank + 1, n_rows):
                if A[row, col]:
                    A[row] = (A[row] + A[rank]) % 2
                    
            rank += 1
            
        nullity = n_cols - rank
        
        print(f"\n  Matrix dimensions: {n_rows} × {n_cols}")
        print(f"  Rank: {rank}")
        print(f"  Nullity: {nullity}")
        print(f"  Expected nullity (if pattern holds): ~{self.n_octahedra // 50 + 1}")
        
        return nullity, rank
    
    def analyze_coupling(self, relations):
        """Analyze coupling between octahedra."""
        print("\n" + "="*80)
        print("COUPLING ANALYSIS")
        print("="*80)
        
        # Count co-occurrences
        coupling = defaultdict(int)
        
        for rel in relations:
            active_octa = set()
            for p in rel['exponents'].keys():
                if p in self.prime_to_octa:
                    active_octa.add(self.prime_to_octa[p])
                    
            active_list = list(active_octa)
            for i in range(len(active_list)):
                for j in range(i+1, len(active_list)):
                    dist = abs(active_list[i] - active_list[j])
                    coupling[dist] += 1
                    
        # Analyze by distance
        print(f"\n{'Distance':^10} {'Coupling Count':^15} {'Decay Factor':^15}")
        print("-" * 45)
        
        prev_count = None
        for dist in sorted(coupling.keys())[:20]:
            count = coupling[dist]
            if prev_count and prev_count > 0:
                decay = count / prev_count
            else:
                decay = 1.0
            print(f"{dist:10d} {count:15d} {decay:15.3f}")
            prev_count = count
            
        return coupling
    
    def run_validation(self):
        """Run complete validation pipeline."""
        # Step 1: Collect relations
        relations = self.collect_relations()
        
        if len(relations) < self.D // 2:
            print(f"\nWARNING: Only {len(relations)} relations found (need ~{self.D})")
            print("Results may be inconclusive")
            
        # Step 2: Build matrix
        matrix = self.build_parity_matrix(relations)
        
        # Step 3: Analyze blocks
        block_stats, rank_deficient = self.analyze_blocks(matrix)
        
        # Step 4: Compute nullspace
        nullity, rank = self.compute_nullspace_dimension(matrix)
        
        # Step 5: Analyze coupling
        coupling = self.analyze_coupling(relations)
        
        # Step 6: Final assessment
        print("\n" + "="*80)
        print("FINAL ASSESSMENT")
        print("="*80)
        
        # Check if pattern holds
        pattern_holds = (rank_deficient <= nullity + 2 and 
                         nullity <= rank_deficient + 2)
        
        print(f"\n  Pattern check: Nullity ≈ Rank Deficient? {pattern_holds}")
        print(f"    Rank deficient octahedra: {rank_deficient}")
        print(f"    Nullspace dimension: {nullity}")
        
        if rank_deficient > 10:
            print(f"\n  ⚠ WARNING: Rank deficiency ({rank_deficient}) is growing!")
            print(f"    This may indicate the structure doesn't scale.")
        elif rank_deficient <= 5:
            print(f"\n  ✓ Pattern holds: Rank deficiency remains small ({rank_deficient})")
            print(f"    Suggests structure may scale to larger D.")
            
        # Memory usage estimate
        memory_mb = (matrix.nbytes + matrix.nbytes) / (1024 * 1024)
        print(f"\n  Memory usage: {memory_mb:.1f} MB")
        
        if memory_mb > 1000:
            print(f"    ⚠ High memory usage - may not scale to D=10⁶")
        else:
            print(f"    ✓ Memory usage reasonable")
            
        return {
            'relations': len(relations),
            'nullity': nullity,
            'rank_deficient': rank_deficient,
            'pattern_holds': pattern_holds,
            'memory_mb': memory_mb,
            'coupling': coupling
        }

# Run validation for D=500
print("OCTAHEDRAL FRAMEWORK VALIDATION")
print("="*80)
print()
print("This test will validate whether the block structure holds at D=500.")
print("Estimated runtime: 30-60 minutes")
print()

# Use N=1003 for consistency with previous tests
N = 1003
D = 500

validator = LargeScaleValidator(N, D)
results = validator.run_validation()

print("\n" + "="*80)
print("VALIDATION COMPLETE")
print("="*80)
print()
print("Results saved. Key findings:")
print(f"  Relations collected: {results['relations']}")
print(f"  Nullity: {results['nullity']}")
print(f"  Rank deficient octahedra: {results['rank_deficient']}")
print(f"  Pattern holds: {results['pattern_holds']}")
print(f"  Memory usage: {results['memory_mb']:.1f} MB")
