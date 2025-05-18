from __future__ import annotations

from sympy import Basic

from estimates.basic import Type, describe
from estimates.test import test

## Proof states describe the current state of a proof (a list of hypotheses and a goal).  The hypotheses are a dictionary of string-Basic pairs that match a hypothesis name to the sympy basic class they represent.  The goals are stored as sympy basic classes.

## Goals should be predicate objects.  Hypotheses can be either predicates or variables.  In the latter case, the name of the hypothesis should match the name of the variable.


class ProofState:
    goal: Basic                    # The goal of the proof state
    hypotheses: dict[str, Basic]   # A dictionary of hypotheses, where the key is the name of the hypothesis and the value is the sympy basic class it represents

    def __init__(self, goal: Basic, hypotheses: dict[str, Basic] | None = None) -> None:
        """
        Initialize a proof state with a goal, and an optional list of hypotheses.
        """
        self.goal = goal
        self.hypotheses = hypotheses if hypotheses is not None else {}

    def set_goal(self, goal: Basic) -> None:
        """Set the goal of the proof state."""
        self.goal = goal

    def copy(self) -> ProofState:
        """
        Create a copy of the proof state.
        """
        return ProofState(self.goal, self.hypotheses.copy())

    def eq(self, other: ProofState) -> bool:
        """
        Check if two proof states are equal.
        """
        return self.goal == other.goal and self.hypotheses == other.hypotheses

    def new(self, name: str) -> str:
        """returns the first unused version of name (adding primes as needed) that isn't already claimed as a hypothesis"""
        new_name = name
        while new_name in self.hypotheses:
            new_name += "'"
        return new_name

    def remove_hypothesis(self, name: str) -> None:
        """Remove a hypothesis from the proof state."""
        assert name in self.hypotheses, f"Hypothesis {name} not found in proof state."
        if isinstance(self.hypotheses[name], Type):
            raise ValueError(
                f"Hypothesis {name} is a variable declaration.  Removing variables is currently unimplemented."
            )
            # TODO: allow for variables to be removed if no hypotheses or goals uses them
        else:
            del self.hypotheses[name]

    def get_hypothesis(self, name: str) -> Basic:
        """Get a hypothesis from the proof state."""
        assert name in self.hypotheses, f"Hypothesis {name} not found in proof state."
        obj = self.hypotheses[name]
        if isinstance(obj, Type):
            raise ValueError(
                f"Hypothesis {name} is a variable declaration.  Use get_var() to get the variable."
            )
        return self.hypotheses[name]

    def get_var(self, name: str) -> Basic:
        """Get a variable from the proof state."""
        assert name in self.hypotheses, f"Variable {name} not found in proof state."
        obj = self.hypotheses[name]
        if isinstance(obj, Type):
            return obj.var()
        else:
            raise ValueError(
                f"Hypothesis {name} is a hypothesis, not a variable.  Use get_hypothesis() to get the hypothesis."
            )

    def get_var_name(self, var: Basic) -> str:
        """Get the name of a variable from the proof state."""
        for name, obj in self.hypotheses.items():
            if isinstance(obj, Type) and obj.var() == var:
                return name
        raise ValueError(f"Variable {var} not found in proof state.")

    def get_all_vars(self) -> set[Basic]:
        """Get all variables from the proof state."""
        vars = set()
        for obj in self.hypotheses.values():
            if isinstance(obj, Type):
                vars.add(obj.var())
        return vars

    def rename_hypothesis(self, old_name: str, new_name: str) -> str:
        """Rename a hypothesis in the proof state."""
        if old_name in self.hypotheses:
            if new_name in self.hypotheses:
                raise ValueError(
                    f"Hypothesis {new_name} already exists.  Please choose a different name."
                )
            else:
                if isinstance(self.hypotheses[old_name], Type):
                    raise ValueError(
                        f"Hypothesis {old_name} is a variable declaration.  Renaming variables is currently unimplemented."
                    )
                    # May be best to keep this functionality disabled, as things get confusing if the proofstate name and the sympy name for a variable are permitted to diverge.  Alternatively, if one renames a proofstate variable, one could create a sympy variable with the new name and swap all occurrences of the old name with the new name.  This may be a bit of a pain to implement, though.
                else:
                    hyp = self.hypotheses[old_name]
                    del self.hypotheses[old_name]
                    new_name = self.new(new_name)
                    self.hypotheses[new_name] = hyp
                    return new_name
        else:
            raise ValueError(f"Hypothesis {old_name} not found in proof state.")

    def new_hypothesis(self, name: str, hypothesis: Basic) -> str:
        """Add a new hypothesis to the proof state, updating the name if necessary.  Returns the name of the hypothesis."""
        name = self.new(name)
        self.hypotheses[name] = hypothesis
        return name

    def list_hypotheses(self, variables: bool = False) -> list[Basic]:
        """Return a list of the names of the hypotheses in the proof state.  By default, variable declarations are excluded."""
        if variables:
            return list(self.hypotheses.values())
        else:
            return [
                var for var in self.hypotheses.values() if not isinstance(var, Type)
            ]

    def test(self, goal: Basic, verbose: bool = True) -> bool:
        """
        Check if a goal follows immediately from the stated hypotheses, including from the implicit ones.
        """
        return test(self.hypotheses.values(), goal, verbose)

    def __str__(self) -> str:
        output = []
        for name, hypothesis in self.hypotheses.items():
            output.append(describe(name, hypothesis))
        output.append(f"|- {self.goal}")
        return "\n".join(output)
