from typing import Dict, List, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class ArchitectureContract(BaseModel):
    id: str
    name: str
    description: str
    required_fields: List[str]
    optional_fields: List[str]
    allowed_tools: str = "any" # "any", "none", or specific list
    template_dir: str

class ArchitectureRegistry:
    """
    Single Source of Truth for Architecture Definitions and Contracts.
    Replaces hardcoded logic throughout the application.
    """
    _architectures: Dict[str, ArchitectureContract] = {}

    @classmethod
    def initialize_default(cls):
        if cls._architectures:
            return
            
        cls.register(ArchitectureContract(
            id="single-agent",
            name="Single Agent",
            description="A standard agent executing tasks procedurally.",
            required_fields=[],
            optional_fields=["tools", "skills"],
            template_dir="single_agent"
        ))
        
        cls.register(ArchitectureContract(
            id="sequential",
            name="Sequential Workflow",
            description="A pipeline of agents that execute one after another.",
            required_fields=["workflow"],
            optional_fields=["shared_tools", "skills"],
            template_dir="sequential"
        ))
        
        cls.register(ArchitectureContract(
            id="parallel",
            name="Parallel Workflow",
            description="Multiple agents working independently at the same time.",
            required_fields=["workers"],
            optional_fields=["shared_tools", "skills"],
            template_dir="parallel"
        ))
        
        cls.register(ArchitectureContract(
            id="router",
            name="Router",
            description="Analyzes intent and routes to a specific worker.",
            required_fields=["routes"],
            optional_fields=["skills"],
            template_dir="router"
        ))

        cls.register(ArchitectureContract(
            id="orchestrator-workers",
            name="Orchestrator Workers",
            description="A central manager divides tasks among worker nodes.",
            required_fields=["workers"],
            optional_fields=["shared_tools", "max_iterations"],
            template_dir="orchestrator_workers"
        ))

        cls.register(ArchitectureContract(
          id="supervisor",
          name="Supervisor",
          description="A supervisor coordinates specialized workers and decides which one acts.",
          required_fields=["workers"],
          optional_fields=["shared_tools", "max_iterations", "delegation_policy"],
          template_dir="supervisor"
      ))

        cls.register(ArchitectureContract(
          id="evaluator-optimizer",
          name="Evaluator Optimizer",
          description="A generator produces output and an evaluator iteratively improves it.",
          required_fields=["generator", "evaluator"],
          optional_fields=["max_iterations", "acceptance_threshold"],
          template_dir="evaluator_optimizer"
          ))

        cls.register(ArchitectureContract(
          id="handoff",
          name="Handoff",
          description="One agent transfers complete responsibility to another specialist.",
          required_fields=["agents"],
          optional_fields=["handoff_rules", "fallback", "termination_condition"],
          template_dir="handoff"
          ))

    @classmethod
    def register(cls, contract: ArchitectureContract):
        cls._architectures[contract.id] = contract

    @classmethod
    def get_contract(cls, arch_id: str) -> Optional[ArchitectureContract]:
        cls.initialize_default()
        return cls._architectures.get(arch_id)

    @classmethod
    def list_all_architectures(cls) -> List[str]:
        cls.initialize_default()
        return list(cls._architectures.keys())
