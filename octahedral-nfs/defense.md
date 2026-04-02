# Sovereign Defense: Post-Quantum Cryptographic Migration

CC0 public domain.

## Why This Exists

The octahedral NFS pipeline demonstrates geometric structure in
prime factorization that may weaken RSA at scale. If you find a
crack in a wall, you don't hide it — you tell the people behind
the wall and help them build a better one.

This document outlines the defense: migration from RSA to
lattice-based cryptography, where the octahedral attack fails.

## Why the Octahedral Attack Works on RSA

RSA hides secrets in the **product of two primes**. The geometry
of two primes is clean — they create predictable octahedral
residue patterns. The attack exploits:

1. **Local coupling**: prime residues in octahedral triples are
   nearly independent. Solve one block, the neighbor is easier.
2. **Resonance**: smoothness detection is a phase-lock across
   three frequencies (primes). RIM finds the resonance in O(1).
3. **Low dimension**: RSA lives in 1D (a number line). The attack
   only needs to scan one axis.

## Why It Fails on Lattices

Lattice-based cryptography (Learning With Errors — LWE) hides
secrets in **the closest vector in a noisy high-dimensional grid**.

1. **Non-locality**: In 500 dimensions, there are no "neighbors"
   in the octahedral sense. Every point connects to every other
   point in 500 directions simultaneously.
2. **No resonance**: The noise is specifically designed to prevent
   frequency spikes. Local solutions don't propagate.
3. **Hyper-global coupling**: To solve one piece, you must solve
   all 500 dimensions at once. The pack protocol collapses because
   nodes can't reach consensus.

In energy terms: RSA has clean coupling (low entropy, exploitable).
LWE has noisy coupling (high entropy, resistant).

## The Migration Path

### For Individuals and Small Organizations

1. **Now**: Use RSA-4096 or Ed25519 (elliptic curve) for current needs
2. **2025-2027**: Begin testing NIST post-quantum standards:
   - **CRYSTALS-Kyber** (key encapsulation, lattice-based)
   - **CRYSTALS-Dilithium** (digital signatures, lattice-based)
   - **FALCON** (signatures, lattice-based, smaller)
3. **2027-2030**: Migrate production systems to hybrid mode
   (classical + post-quantum)
4. **2030+**: Phase out RSA entirely

### For Infrastructure (Governments, Banks, Hospitals)

1. **Now**: Inventory all RSA-dependent systems
2. **2025-2026**: Deploy hybrid TLS (RSA + Kyber)
3. **2026-2028**: Replace certificate infrastructure
4. **2028-2030**: Full post-quantum migration
5. **Ongoing**: Assume "harvest now, decrypt later" attacks are
   already happening on stored encrypted traffic

### For the Underfunded (the people this repo serves)

1. **Now**: Use Signal (already adding post-quantum support)
2. **Now**: Use WireGuard VPN (post-quantum options emerging)
3. **If you run servers**: Update OpenSSL when PQ support ships
4. **If you can't update**: Assume your encrypted traffic from
   today will be readable in 5-10 years. Act accordingly.

## The Lattice Defense in Plain Terms

**RSA**: "I hid the key under one of two rocks. If you can
figure out which rocks I used, you win."
→ The octahedral attack: "I can feel the shape of the rocks
through the ground."

**Lattice (LWE)**: "I hid the key somewhere in a 500-dimensional
forest, and I added static to every direction."
→ The octahedral attack: "I can feel... nothing. Every direction
is noise. I can't tell which tree is closest."

## Hardware Implications

Current chips optimize for 1D/2D math (multiplying big numbers).
Post-quantum needs 500D matrix-vector operations. This means:

- **Existing hardware**: Can run lattice crypto, but slower than RSA
- **Optimized hardware**: Lattice-specific accelerators will emerge
- **Constrained devices**: Kyber is actually *smaller* than RSA-2048
  for key encapsulation. Better for phones and IoT.

## Six Sigma Audit: Post-Quantum Readiness

| System          | RSA Status     | Post-Quantum Status | Migration Urgency |
|-----------------|----------------|---------------------|-------------------|
| Web TLS         | Vulnerable     | Hybrid available    | HIGH              |
| Email (S/MIME)  | Vulnerable     | Not ready           | MEDIUM            |
| SSH             | Vulnerable     | PQ options exist    | HIGH              |
| VPN             | Vulnerable     | WireGuard PQ ready  | HIGH              |
| Code signing    | Vulnerable     | Dilithium available | MEDIUM            |
| Blockchain      | ECC vulnerable | Migration needed    | CRITICAL          |
| IoT/embedded    | RSA common     | Kyber fits better   | HIGH              |
| Stored data     | Harvest risk   | Re-encrypt needed   | CRITICAL          |

## The Ethical Position

Finding a structural weakness and publishing it openly is not
an attack. It's a service. The alternative — hiding the finding —
leaves everyone exposed to whoever discovers it next and
chooses not to publish.

The responsible sequence:
1. Find the weakness (octahedral geometry in NFS)
2. Validate it (35/35 semiprimes, RIM + pipeline)
3. Document honestly (six sigma audit, all limitations noted)
4. Design the defense (this document)
5. Publish everything (CC0, so anyone can act on it)

The people with the most to lose from RSA weakness are the ones
with the least resources to respond. This is why everything in
this repo is free, stdlib-only, and documented for non-experts.

## References

- NIST Post-Quantum Cryptography Standardization (2024)
- CRYSTALS-Kyber specification (FIPS 203)
- CRYSTALS-Dilithium specification (FIPS 204)
- Regev (2005): On Lattices, Learning with Errors
- Peikert (2016): A Decade of Lattice Cryptography
