# KnowledgeDNA

Knowledge ancestry modeled as energy field propagation.

CC0 public domain.

## What This Does

Standard knowledge attribution is linear: A cited B. This system
treats knowledge as a state variable that propagates through a
directed graph. Influence flows backward (who still shapes this?)
and forward (where does this go?), weighted by transfer efficiency,
phase alignment, and time decay.

The question changes from "who contributed" to "what is still
actively shaping this state."

## Quick Start

```bash
python -m KnowledgeDNA.knowledge_dna
```

This builds the seed ancestry (Solar Flux -> Gravity Storage ->
Vacuum Fluctuations -> Forest Piezo Harvest -> Zero-Point Mesh),
runs field traces, cycle analysis, fragility tests, and forward
evolution.

## Import Seed Data

```python
from KnowledgeDNA.knowledge_dna import KnowledgeDNA

dna = KnowledgeDNA()
dna.import_seed_csv("KnowledgeDNA/seed_data.csv")
dna.print_report(target_node=list(dna.graph.nodes)[-1])
```

### CSV Format

```
name,contributors,energy,timestamp,parents,dna_path
Solar Flux Capture,"['Nature/Evolution']",1.0,2026-03-25T21:44:11,[],path
Gravity Storage,"['Galileo', 'User Insight']",1.0,2026-03-25T21:44:11,['Solar Flux Capture'],path
```

## Concepts

### Backward Propagation (Field Trace)

From any node, energy propagates backward through all ancestors,
weighted by edge efficiency and phase:

```
E_parent += E_child * efficiency * phase * decay
```

This produces a field, not a path. All ancestors receive energy
proportional to their actual contribution.

### Forward Propagation

Energy flows parent -> child along edges. Models how influence
spreads forward in time. Run multiple steps to see which nodes
accumulate energy and which dissipate.

### Time Decay

```
E_decayed = E * exp(-lambda * dt)
```

Recent knowledge has more influence. The decay rate controls how
fast old, unreinforced knowledge fades.

### Phase

Edges carry a phase value (default 1.0):
- `phase = 1.0`: aligned, constructive influence
- `phase = -1.0`: opposed, destructive interference
- `phase = 0.5`: partial alignment

Phase models whether two ideas reinforce or conflict.

### Cycle Analysis

Cycles in the graph have a gain:

```
C = product(efficiency_i * phase_i) for edges in cycle
```

- `|C| ~ 1`: stable loop (persistent structure)
- `|C| < 1`: dissipative (knowledge decays around the loop)
- `|C| > 1`: runaway amplification (unstable)

### Fragility Analysis

Remove each node, measure total energy collapse. High collapse
means that node is load-bearing — its removal disrupts the
knowledge field disproportionately.

### Spatial Locality

Nodes have positions. A Gaussian kernel weights propagation by
distance: nearby nodes interact more strongly. `propagate_energy_local()`
and `forward_step_local()` use this.

### Attractors

Run forward propagation multiple steps. Nodes whose energy
stabilizes (variance < tolerance) are attractors — ideas that
persist despite perturbation.

## Files

| File              | Description                        | Dependencies |
|-------------------|------------------------------------|-------------|
| `knowledge_dna.py`| Full engine + demo                | None        |
| `seed_data.csv`   | Seed ancestry data                 | None        |
| `__init__.py`     | Package marker                     | None        |

## API

```python
dna = KnowledgeDNA()

# Build graph
node_id = dna.add_thought("Name", ["contributors"], energy=1.0,
                           parents=[parent_id])

# Backward field trace
field = dna.trace_field(node_id)          # list of {node, name, energy, contributors}

# Forward evolution
dna.forward_step()                        # one step
dna.inject_noise(magnitude=0.05)          # test stability

# Analysis
cycles = dna.analyze_cycles()             # cycle detection + gain
fragility = dna.fragility_test(node_id)   # remove node, measure collapse
attractors = dna.find_attractors()        # stable nodes under forward prop

# Export
dna.export_csv("knowledge_dna.csv")       # full graph
dna.export_field_csv(field, "trace.csv")  # field trace
```

## Relationship to Other Modules

- **sim/cities/coupling.py**: Knowledge decay layers model the same
  phenomenon (embodied knowledge dying with holders) from the city
  resilience perspective. KnowledgeDNA models the ancestry and
  propagation dynamics of that knowledge.

- **sim/seed_protocol.py**: Seed encoding maps identity to 6D space.
  KnowledgeDNA maps knowledge influence to a directed graph. Both
  model how information persists and propagates without central
  coordination.

## Why Stdlib Only

The original version used networkx, pandas, and matplotlib. Those
are useful libraries, but they require pip, which requires internet,
which requires infrastructure. The people studying knowledge loss
and transmission breakdown are often the ones with the least access
to that infrastructure.

This version runs on anything with Python 3.
