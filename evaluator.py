from __future__ import annotations
import time
import json
from typing import Dict, List
from .intent import IntentExtractor
from .design import DesignGenerator
from .validator import ConfigValidator, ValidationResult
from .runtime import ConfigRuntime

class EvaluationEngine:
    def __init__(self, prompts: List[Dict[str, str]]):
        self.prompts = prompts

    def evaluate(self) -> Dict[str, object]:
        metrics = {
            "total": len(self.prompts),
            "success": 0,
            "failures": 0,
            "retries": 0,
            "latencies": [],
            "failure_types": {},
        }
        for item in self.prompts:
            start = time.time()
            prompt = item["prompt"]
            summary = self.run_prompt(prompt)
            latency = time.time() - start
            metrics["latencies"].append(latency)
            if summary["success"]:
                metrics["success"] += 1
            else:
                metrics["failures"] += 1
                metrics["failure_types"][summary["failure_type"]] = metrics["failure_types"].get(summary["failure_type"], 0) + 1
            metrics["retries"] += summary["retry_count"]
        metrics["average_latency"] = sum(metrics["latencies"]) / len(metrics["latencies"]) if metrics["latencies"] else 0
        metrics["retry_rate"] = metrics["retries"] / metrics["total"] if metrics["total"] else 0
        return metrics

    def run_prompt(self, prompt: str) -> Dict[str, object]:
        intent = IntentExtractor.parse(prompt)
        if intent.needs_clarification:
            return {"success": False, "retry_count": 0, "failure_type": "clarification_required"}
        try:
            config = DesignGenerator.create(intent)
        except Exception as exc:
            return {"success": False, "retry_count": 0, "failure_type": "design_failure", "error": str(exc)}
        validation = ConfigValidator.validate(config)
        retry_count = 1 if validation.repairs else 0
        if not validation.valid and not validation.repairs:
            return {"success": False, "retry_count": retry_count, "failure_type": "validation_failure"}
        runtime = ConfigRuntime(config)
        simulate_results = runtime.simulate()
        if not simulate_results.get("health") or not simulate_results.get("config"):
            return {"success": False, "retry_count": retry_count, "failure_type": "runtime_failure"}
        return {"success": True, "retry_count": retry_count, "failure_type": "none", "simulate_results": simulate_results}

    @classmethod
    def load_prompts(cls, path: str) -> List[Dict[str, str]]:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
