import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from core.architecture_registry import ArchitectureRegistry
from core.errors import GenerationError 
from models import AgentSpec
import logging

logger = logging.getLogger(__name__)

class TemplateResolver:
    """
    Renders standard templates based on Architecture Contracts.
    No complex if/else architecture logic exists here.
    """
    def __init__(self, templates_dir: str = None):
        if templates_dir is None:
            templates_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "templates"))
            
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape()
        )

    def render_agent_files(self, spec: AgentSpec, dest_dir: str):
        """
        Renders all required files for an AgentSpec based on its Architecture Contract.
        Throws GenerationError (from pipeline error model) if rendering fails.
        """
        contract = ArchitectureRegistry.get_contract(spec.architecture)
        if not contract:
            from core.errors import GenerationError
            raise GenerationError(f"Architecture '{spec.architecture}' has no defined contract.")
            
        arch_dir = contract.template_dir
        
        try:
            # Render agent.py
            agent_template = self.env.get_template(f"{arch_dir}/agent.py.j2")
            agent_code = agent_template.render(spec=spec)
            
            with open(os.path.join(dest_dir, "agent.py"), "w", encoding="utf-8") as f:
                f.write(agent_code)
                
            # Render README
            try:
                readme_template = self.env.get_template(f"{arch_dir}/README.md.j2")
                readme_code = readme_template.render(spec=spec)
                with open(os.path.join(dest_dir, "README.md"), "w", encoding="utf-8") as f:
                    f.write(readme_code)
            except Exception:
                # README is optional
                pass
                
            # If there are workers, dynamically generate worker nodes
            if spec.workers:
                workers_dir = os.path.join(dest_dir, "workers")
                os.makedirs(workers_dir, exist_ok=True)
                
                try:
                    worker_template = self.env.get_template(f"{arch_dir}/worker.py.j2")
                    for worker in spec.workers:
                        w_code = worker_template.render(spec=spec, worker_name=worker)
                        with open(os.path.join(workers_dir, f"{worker}.py"), "w", encoding="utf-8") as f:
                            f.write(w_code)
                except Exception as e:
                    logger.warning(f"Failed to generate worker files: {e}")

        except Exception as e:
            from core.errors import GenerationError
            raise GenerationError(f"Jinja template generation failed: {e}")
