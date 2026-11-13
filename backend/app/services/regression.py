from __future__ import annotations

import datetime
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.agents.reference import ReferenceToolAgent
from app.benchmarks.pack import ChallengePack, list_packs, load_pack_from_file
from app.faults.engine import FaultConfig, FaultKind
from app.services.runner import ReliabilityRunner, ReliabilityScorecard


class RegressionCase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pack_id: str
    agent_name: str
    seed: int
    fault_kind: str
    at_step: Optional[int] = None
    tool: Optional[str] = None
    expected_failure_category: str
    description: str = ""
    status: str = "STILL_FAILING"  # FIXED or STILL_FAILING
    last_replayed_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())


class RegressionStore:
    """In-memory and file-backed regression gate registry.
    Starts completely clean without fictional default cases.
    """

    def __init__(self):
        self._cases: Dict[str, RegressionCase] = {}

    def list_cases(self) -> List[RegressionCase]:
        return list(self._cases.values())

    def get_case(self, case_id: str) -> Optional[RegressionCase]:
        return self._cases.get(case_id)

    def add_case(self, case: RegressionCase) -> RegressionCase:
        self._cases[case.id] = case
        return case

    def seed_fixture_case(self) -> RegressionCase:
        """Utility for test suites or manual onboarding to seed an isolated test case."""
        case = RegressionCase(
            id="reg-flaky-triage-tool-contract",
            pack_id="flaky_test_triage",
            agent_name="fragile",
            seed=42,
            fault_kind="TOOL_ERROR",
            at_step=3,
            tool="update_quarantine_config",
            expected_failure_category="TOOL_CONTRACT",
            description="Fragile agent unhandled crash when quarantine tool fails",
            status="STILL_FAILING",
        )
        self._cases[case.id] = case
        return case

    def replay_case(
        self,
        case_id: str,
        runner_agent_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        case = self._cases.get(case_id)
        if not case:
            raise KeyError(f"Regression case {case_id} not found")

        # Load pack
        pack_path = f"benchmark_tasks/packs/{case.pack_id}.yaml"
        pack = load_pack_from_file(pack_path)

        agent_to_test = runner_agent_name or case.agent_name
        agent = ReferenceToolAgent(profile=agent_to_test)
        runner = ReliabilityRunner(seed=case.seed)

        fault = FaultConfig(
            kind=FaultKind(case.fault_kind),
            at_step=case.at_step,
            tool=case.tool,
            probability=1.0,
        )

        scorecard = runner.run_pack(pack=pack, agent=agent, k=1, fault=fault)

        # Check if the regression reproduces
        failed = scorecard.pass_rate < 1.0
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        case.last_replayed_at = now_str

        # If it failed with the expected category, it's still failing (regression reproduced)
        # If it passed, it is FIXED!
        if scorecard.pass_rate == 1.0:
            case.status = "FIXED"
        else:
            case.status = "STILL_FAILING"

        return {
            "case_id": case.id,
            "pack_id": case.pack_id,
            "tested_agent": agent_to_test,
            "status": case.status,
            "pass_rate": scorecard.pass_rate,
            "observed_taxonomy": scorecard.taxonomy_counts,
            "replayed_at": now_str,
            "trials": scorecard.trial_results,
        }

    def replay_all(self, target_agent: Optional[str] = None) -> Dict[str, Any]:
        results = []
        still_failing = 0
        fixed = 0

        for case_id in list(self._cases.keys()):
            res = self.replay_case(case_id, runner_agent_name=target_agent)
            results.append(res)
            if res["status"] == "FIXED":
                fixed += 1
            else:
                still_failing += 1

        return {
            "total": len(self._cases),
            "still_failing": still_failing,
            "fixed": fixed,
            "cases": results,
            "replayed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }


regression_store = RegressionStore()

