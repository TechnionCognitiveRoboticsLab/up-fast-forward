import pkg_resources
import sys
import unified_planning as up
from typing import Callable, Iterator, IO, List, Optional, Tuple, Union
from unified_planning.model import ProblemKind
from unified_planning.engines import OptimalityGuarantee
from unified_planning.engines import PlanGenerationResultStatus as ResultStatus
from unified_planning.engines import PDDLAnytimePlanner, PDDLPlanner
from unified_planning.engines import OperationMode, Credits
from unified_planning.engines.results import LogLevel, LogMessage, PlanGenerationResult

credits = {
    "name": "Fast Forward",
    "author": "UPF Wrapper by Erez Karpas, FF planner by Joerg Hoffmann",
    "contact": "karpase@technion.ac.il (for UP integration)",
    "website": "https://fai.cs.uni-saarland.de/hoffmann/ff.html",
    "license": "GPLv3",
    "short_description": "Fast Forward is a domain-independent classical planning system.",
    "long_description": "Fast Forward is a domain-independent classical planning system.",
}



class FastForwardPDDLPlanner(PDDLPlanner):
    def __init__(
        self
    ):
        PDDLPlanner.__init__(self)
        

    @property
    def name(self) -> str:
        return "Fast Forward"

    def _get_cmd(
        self, domain_filename: str, problem_filename: str, plan_filename: str) -> List[str]:
        ff_binary = pkg_resources.resource_filename(
            __name__, "FF-v2.3/ff"
        )        
        cmd += [ff_binary, "-o", domain_filename, "-f", problem_filename]        
        return cmd
    
    def _result_status(
        self,
        problem: "up.model.Problem",
        plan: Optional["up.plans.Plan"],
        retval: int = None,  # Default value for legacy support
        log_messages: Optional[List[LogMessage]] = None,
    ) -> "up.engines.results.PlanGenerationResultStatus":
        if retval is None:  # legacy support
            return ResultStatus.UNSOLVABLE_INCOMPLETELY            
        if retval == 0:            
            return ResultStatus.SOLVED_SATISFICING
        else:
            return ResultStatus.UNSUPPORTED_PROBLEM

    @staticmethod
    def get_credits(**kwargs) -> Optional["Credits"]:
        c = Credits(**credits)
        details = [
            c.long_description,
            "The default configuration uses the FF heuristic by Jörg Hoffmann and",
            "the landmark heuristic by Silvia Richter and Matthias Westphal.",
        ]
        c.long_description = " ".join(details)
        return c

    def _starting_plan_str(self) -> str:
        return "ff: found legal plan as follows"

    def _ending_plan_str(self) -> str:
        return "time spent:"

    def _parse_plan_line(self, plan_line: str) -> str:
        if plan_line.startswith("[t="):
            return ""
        return "(%s)" % plan_line.split("(")[0].strip()

    @staticmethod
    def satisfies(optimality_guarantee: "OptimalityGuarantee") -> bool:
        if optimality_guarantee == OptimalityGuarantee.SATISFICING:
            return True
        return False

    @staticmethod
    def supported_kind() -> "ProblemKind":
        supported_kind = ProblemKind()
        supported_kind.set_problem_class("ACTION_BASED")
        supported_kind.set_typing("FLAT_TYPING")
        supported_kind.set_typing("HIERARCHICAL_TYPING")
        supported_kind.set_conditions_kind("NEGATIVE_CONDITIONS")
        supported_kind.set_conditions_kind("DISJUNCTIVE_CONDITIONS")
        supported_kind.set_conditions_kind("EXISTENTIAL_CONDITIONS")
        supported_kind.set_conditions_kind("UNIVERSAL_CONDITIONS")
        supported_kind.set_conditions_kind("EQUALITIES")
        supported_kind.set_effects_kind("CONDITIONAL_EFFECTS")
        supported_kind.set_effects_kind("STATIC_FLUENTS_IN_BOOLEAN_ASSIGNMENTS")
        supported_kind.set_effects_kind("FLUENTS_IN_BOOLEAN_ASSIGNMENTS")
        supported_kind.set_effects_kind("FORALL_EFFECTS")
        supported_kind.set_quality_metrics("ACTIONS_COST")
        supported_kind.set_actions_cost_kind("STATIC_FLUENTS_IN_ACTIONS_COST")
        supported_kind.set_quality_metrics("PLAN_LENGTH")
        return supported_kind

    @staticmethod
    def supports(problem_kind: "ProblemKind") -> bool:
        return problem_kind <= FastDownwardPDDLPlanner.supported_kind()

    @staticmethod
    def ensures(anytime_guarantee: up.engines.AnytimeGuarantee) -> bool:
        if anytime_guarantee == up.engines.AnytimeGuarantee.INCREASING_QUALITY:
            return True
        return False


class FastDownwardOptimalPDDLPlanner(FastDownwardMixin, PDDLPlanner):
    def __init__(self, log_level: str = "info"):
        PDDLPlanner.__init__(self)
        FastDownwardMixin.__init__(
            self, fast_forward_search_config="astar(lmcut())", log_level=log_level
        )
        self._guarantee_no_plan_found = ResultStatus.UNSOLVABLE_PROVEN
        self._guarantee_metrics_task = ResultStatus.SOLVED_OPTIMALLY

    @property
    def name(self) -> str:
        return "Fast Downward (with optimality guarantee)"

    @staticmethod
    def get_credits(**kwargs) -> Optional["Credits"]:
        c = Credits(**credits)
        details = [
            c.long_description,
            "The optimal engine uses the LM-Cut heuristic by",
            "Malte Helmert and Carmel Domshlak.",
        ]
        c.long_description = " ".join(details)
        return c

    @staticmethod
    def supported_kind() -> "ProblemKind":
        supported_kind = ProblemKind()
        supported_kind.set_problem_class("ACTION_BASED")
        supported_kind.set_typing("FLAT_TYPING")
        supported_kind.set_typing("HIERARCHICAL_TYPING")
        supported_kind.set_conditions_kind("NEGATIVE_CONDITIONS")
        supported_kind.set_conditions_kind("DISJUNCTIVE_CONDITIONS")
        supported_kind.set_conditions_kind("EXISTENTIAL_CONDITIONS")
        supported_kind.set_conditions_kind("UNIVERSAL_CONDITIONS")
        supported_kind.set_conditions_kind("EQUALITIES")
        supported_kind.set_quality_metrics("ACTIONS_COST")
        supported_kind.set_actions_cost_kind("STATIC_FLUENTS_IN_ACTIONS_COST")
        supported_kind.set_quality_metrics("PLAN_LENGTH")
        return supported_kind

    @staticmethod
    def supports(problem_kind: "ProblemKind") -> bool:
        return problem_kind <= FastDownwardOptimalPDDLPlanner.supported_kind()

    @staticmethod
    def satisfies(optimality_guarantee: OptimalityGuarantee) -> bool:
        return True
