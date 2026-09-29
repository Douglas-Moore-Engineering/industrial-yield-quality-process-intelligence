"""Reference shadow lifecycle and evidence ledger; no network/control integrations.

This local ledger is not a multi-user authentication service or immutable audit store.
Production requires an authenticated caller and separately governed persistence.
"""
import hashlib
import json
import sqlite3
from datetime import datetime, timezone

import numpy as np

from iyqpis.intelligence import fingerprint, metrics, transform, verify_bundle


class Ledger:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS models(id TEXT PRIMARY KEY, path TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS active(slot INTEGER PRIMARY KEY CHECK(slot=1), model TEXT REFERENCES models(id));
        CREATE TABLE IF NOT EXISTS events(sequence INTEGER PRIMARY KEY, kind TEXT NOT NULL,
          payload TEXT NOT NULL, previous_hash TEXT NOT NULL, hash TEXT UNIQUE NOT NULL);
        CREATE TABLE IF NOT EXISTS evidence(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS decisions(evidence_id TEXT PRIMARY KEY REFERENCES evidence(id),
          disposition TEXT NOT NULL, actor TEXT NOT NULL, rationale TEXT NOT NULL, modified_action TEXT);
        """)

    def close(self):
        self.db.close()

    def _append(self, kind, payload):
        previous = self.db.execute("SELECT hash FROM events ORDER BY sequence DESC LIMIT 1").fetchone()
        previous = previous[0] if previous else "0" * 64
        body = json.dumps(payload, sort_keys=True, allow_nan=False)
        value = hashlib.sha256((previous + kind + body).encode()).hexdigest()
        self.db.execute("INSERT INTO events(kind,payload,previous_hash,hash) VALUES(?,?,?,?)", (kind, body, previous, value))

    def register(self, path):
        model = verify_bundle(path)
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO models VALUES(?,?)", (model["model_id"], str(path.resolve())))
            self._append("REGISTER", {"model_id": model["model_id"], "mode": "SHADOW"})
        return model["model_id"]

    def activate(self, model_id, mode="SHADOW"):
        if mode != "SHADOW":
            raise PermissionError("Reference environment cannot promote production/advisory models")
        row = self.db.execute("SELECT path FROM models WHERE id=?", (model_id,)).fetchone()
        if not row or verify_bundle(row[0])["model_id"] != model_id:
            raise ValueError("Unknown or corrupt release")
        with self.db:
            old = self.db.execute("SELECT model FROM active WHERE slot=1").fetchone()
            self.db.execute("INSERT OR REPLACE INTO active VALUES(1,?)", (model_id,))
            self._append("ACTIVATE", {"model_id": model_id, "previous": old[0] if old else None, "mode": mode})

    def rollback(self):
        events = self.db.execute("SELECT payload FROM events WHERE kind='ACTIVATE' ORDER BY sequence DESC").fetchall()
        if not events or not json.loads(events[0][0])["previous"]:
            raise ValueError("No previous release")
        self.activate(json.loads(events[0][0])["previous"])

    def record_evidence(self, evidence):
        evidence_id = fingerprint(evidence)
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO evidence VALUES(?,?)", (evidence_id, json.dumps(evidence, sort_keys=True)))
            self._append("EVIDENCE", {"evidence_id": evidence_id})
        return evidence_id

    def review(self, evidence_id, disposition, actor, rationale, modified_action=None):
        if disposition not in {"APPROVE", "MODIFY", "REJECT", "INVESTIGATE"} or not actor.strip() or not rationale.strip():
            raise ValueError("Explicit disposition, operator identifier and rationale required")
        if disposition == "MODIFY" and not (modified_action and modified_action.strip()):
            raise ValueError("Modified review proposal required; it does not authorize a control action")
        with self.db:
            self.db.execute("INSERT INTO decisions VALUES(?,?,?,?,?)", (evidence_id, disposition, actor, rationale, modified_action))
            self._append("REVIEW", {"evidence_id": evidence_id, "disposition": disposition,
                                   "actor": actor, "rationale": rationale, "modified_action": modified_action,
                                   "control_action_authorized": False})

    def verify_audit(self):
        previous = "0" * 64
        for kind, body, parent, actual in self.db.execute("SELECT kind,payload,previous_hash,hash FROM events ORDER BY sequence"):
            expected = hashlib.sha256((previous + kind + body).encode()).hexdigest()
            if parent != previous or actual != expected:
                raise ValueError("Audit chain mismatch")
            previous = actual
        return previous


def process_baseline(values):
    x = np.asarray(values, dtype=float)
    if len(x) < 20 or not np.isfinite(x).all() or x.std(ddof=1) == 0:
        raise ValueError("Need 20 finite, variable reference measurements")
    return {"mean": float(x.mean()), "std": float(x.std(ddof=1)), "n": len(x)}


def process_monitor(baseline, values):
    x = np.asarray(values, dtype=float)
    if not np.isfinite(x).all():
        raise ValueError("Invalid process measurements")
    z = (x - baseline["mean"]) / baseline["std"]
    # Illustrative three-sigma monitoring, not control limits approved by a plant.
    return {"three_sigma_indices": np.where(np.abs(z) > 3)[0].tolist(),
            "mean_standardized_shift": float(z.mean()) if len(z) else None,
            "scope": "reference individual-measurement monitoring; not Xbar-R validation"}


def monitor_model(model, x, observed=None):
    from iyqpis.intelligence import probabilities
    x = np.asarray(x, dtype=float)
    if x.ndim != 2 or x.shape[1] != len(model["features"]) or len(x) == 0 or np.isinf(x).any():
        raise ValueError("Invalid monitoring batch")
    z = transform(x, model["preprocessing"])
    missing = float(np.isnan(x).mean())
    outside = float((np.abs(z) > model["guardrails"]["max_abs_standardized_value"]).any(axis=1).mean())
    result = {"rows": len(x), "missing_fraction": missing, "outside_envelope_fraction": outside,
              "max_abs_mean_standardized_shift": float(np.abs(z.mean(axis=0)).max()),
              "warning": missing > .2 or outside > .1,
              "threshold_scope": "illustrative reference thresholds; not plant-approved"}
    if observed is not None:
        y = np.asarray(observed)
        if len(y) != len(x) or not set(y) <= {0, 1}:
            raise ValueError("Invalid matched outcomes")
        result["outcome_metrics"] = metrics(y, probabilities(model, x), model["alert_threshold"])
    return result


def comparable_cases(query, cases, as_of, limit=5):
    """Retrieve prior numeric cases only; no unobserved future outcomes exposed."""
    cutoff = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
    if cutoff.tzinfo is None or limit < 1:
        raise ValueError("Invalid retrieval boundary")
    query = np.asarray(query, dtype=float)
    if not np.isfinite(query).all():
        raise ValueError("Invalid query")
    matches = []
    for case in cases:
        at = datetime.fromisoformat(case["event_time"].replace("Z", "+00:00"))
        if at.tzinfo is None:
            raise ValueError("Case timezone required")
        if at >= cutoff:
            continue
        vector = np.asarray(case["features"], dtype=float)
        if vector.shape != query.shape or not np.isfinite(vector).all():
            raise ValueError("Case feature mismatch")
        matches.append({"case_id": case["case_id"], "distance": float(np.linalg.norm(query-vector))})
    return sorted(matches, key=lambda r: (r["distance"], r["case_id"]))[:limit]


def affected_material(edges, start):
    """Traverse supplied directed genealogy only; absent edges mean unknown coverage."""
    graph = {}
    for edge in edges:
        if not all(edge.get(key) for key in ("parent", "child", "evidence_ref")):
            raise ValueError("Every genealogy edge requires explicit evidence")
        graph.setdefault(edge["parent"], set()).add(edge["child"])
    seen, visiting = set(), set()
    def visit(node):
        if node in visiting:
            raise ValueError("Cyclic material genealogy")
        if node in seen:
            return
        visiting.add(node)
        for child in graph.get(node, ()):
            visit(child)
        visiting.remove(node)
        seen.add(node)
    visit(start)
    seen.remove(start)
    return {"descendants": sorted(seen), "coverage": "supplied_edges_only", "source": start}


def production_gate(evidence):
    required = ("approved_plant", "source_owner", "source_contract", "warning_horizon",
                "temporal_and_group_validation", "quality_thresholds", "security_review",
                "restore_drill", "shadow_acceptance", "canary_acceptance", "human_approval")
    missing = [key for key in required if not evidence.get(key)]
    # References are not verified signatures. This reference implementation cannot grant production authority.
    return {"state": "BLOCKED", "missing": missing,
            "reason": "Reference environment; production authority is not implemented"}
