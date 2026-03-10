# Urban Resilience Simulator

**Standard emergency management models are wrong about where resilience lives.**

They model pipes, generators, and bed counts.
They do not model the humans who operate them under stress,
make decisions about building access,
or choose whether to help a neighbor
or wait for institutional authorization.

This simulator corrects that inversion.

---

## The core argument

Standard models treat suburban, financially-mediated, 
institution-dependent living as the design reference for "normal."

Rural competence and inner-city mutual aid networks — 
the actual load-bearing structure of societal survival — 
are either unmodeled or flagged as vulnerability.

That is upside-down engineering.
Reinforcing non-load-bearing elements (financial products, suburban retail access).
Neglecting load-bearing elements (people who can fix pumps without OEM support,
improvise medical care without supply chains, feed 100 people without a supermarket).

This simulator puts the load paths at Layer Zero.

---

## Architecture

Layer Zero (before infrastructure):
├── CognitiveReadinessLayer   — neuroplasticity as infrastructure
├── DecisionAuthorityNode     — who decides, are they present
└── SocialTrustLayer          — gratitude vs transaction networks
Infrastructure Layers:
├── Water    ├── Food     ├── Energy
├── Medical  ├── Repair   ├── Comms
└── Manufacturing
Institutional Assets:
├── Colleges (labs, dorms, cafeterias as redundancy nodes)
├── Hospitals
├── Cooperatives
└── Industrial
Bias Layer:
├── SuburbanBiasReport        — what the model cannot see and why
├── HiddenVariableLayer       — undocumented competencies by zone
└── ActuarialBlindSpot        — insurance extraction from resilience


Layer Zero modifies all infrastructure timelines.
Social trust and cognitive readiness determine whether
hardware redundancy can actually be activated.

---

## Key findings — Madison WI (first populated city)

| Zone | Runs Forward | Survival Window | Cognitive Layer | Decision Lag |
|------|-------------|-----------------|-----------------|--------------|
| Rural fringe | ✓ YES | ~140h | LOAD_BEARING | 1h |
| Inner city | ✓ YES | ~86h | LOAD_BEARING | 4h |
| Suburban sprawl | ✗ NO | ~14h | FACADE | 36h |

Suburban sprawl has the largest population (160k of 269k)
and the shortest survival window.
Standard models flag rural fringe as high vulnerability.
This model shows it as the primary resilience node.

---

## Usage

```bash
python run.py

Zero dependencies. Phone-operable. Python 3.10+.


Data slots
Fields marked # [POPULATE] accept real local data.
Architecture is complete. Numbers are estimates until populated.
Contribute real data for your city via pull request.

License
CC0 — public domain. No rights reserved.
Use freely. No attribution required.
The knowledge belongs to the people who lived it.

The people with the most operational knowledge
are the least likely to document it —
because documentation is not survival.
This is an attempt to make the invisible visible
before the systems that depend on it fail completely.


