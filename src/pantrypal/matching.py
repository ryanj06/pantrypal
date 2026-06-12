"""Core matching logic for suggesting recipes based on pantry contents."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from pantrypal.recipes import Recipe, normalize_recipe_ingredients
from pantrypal.storage import normalize_name


@dataclass
class RecipeMatch:
    name: str
    have: Dict[str, float] = field(default_factory=dict)
    missing: Dict[str, float] = field(default_factory=dict)
    insufficient: Dict[str, tuple] = field(default_factory=dict)  # name -> (have, need)

    @property
    def total_ingredients(self) -> int:
        return len(self.have) + len(self.missing) + len(self.insufficient)

    @property
    def num_satisfied(self) -> int:
        return len(self.have)

    @property
    def match_ratio(self) -> float:
        total = self.total_ingredients
        if total == 0:
            return 0.0
        return self.num_satisfied / total

    @property
    def is_makeable(self) -> bool:
        return not self.missing and not self.insufficient


def match_recipe(recipe: Recipe, pantry: Dict[str, float]) -> RecipeMatch:
    """Compare a single recipe's ingredient needs against pantry stock."""
    normalized_pantry = {normalize_name(k): v for k, v in pantry.items()}
    needs = normalize_recipe_ingredients(recipe)

    match = RecipeMatch(name=str(recipe["name"]))
    for ingredient, qty_needed in needs.items():
        have_qty = normalized_pantry.get(ingredient, 0)
        if have_qty <= 0:
            match.missing[ingredient] = qty_needed
        elif have_qty < qty_needed:
            match.insufficient[ingredient] = (have_qty, qty_needed)
        else:
            match.have[ingredient] = qty_needed

    return match


def suggest_recipes(
    recipes: List[Recipe], pantry: Dict[str, float], limit: int = 5
) -> List[RecipeMatch]:
    """Return recipes ranked by how closely they match the pantry.

    Recipes that are fully makeable (no missing/insufficient ingredients)
    are listed first, then recipes are sorted by match ratio descending.
    """
    matches = [match_recipe(r, pantry) for r in recipes]
    matches.sort(key=lambda m: (not m.is_makeable, -m.match_ratio, m.name))
    return matches[:limit]


def shopping_list(matches: List[RecipeMatch]) -> Dict[str, float]:
    """Aggregate missing/insufficient quantities across recipe matches.

    For insufficient ingredients, only the additional amount needed
    (need - have) is included.
    """
    needs: Dict[str, float] = {}
    for match in matches:
        for ingredient, qty in match.missing.items():
            needs[ingredient] = needs.get(ingredient, 0) + qty
        for ingredient, (have, need) in match.insufficient.items():
            additional = need - have
            needs[ingredient] = needs.get(ingredient, 0) + additional
    return needs
