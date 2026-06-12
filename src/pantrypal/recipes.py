"""Recipe database for PantryPal.

Recipes are stored as a list of dicts with the shape:
    {
        "name": str,
        "ingredients": {ingredient_name: quantity_needed, ...},
        "tags": list of strings, e.g. ["vegetarian", "quick"]
    }

Users can extend the recipe list by editing ~/.pantrypal/recipes.json
(created on first run from the built-in defaults below), or via the
`pantry add-recipe` command.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from pantrypal.storage import _data_dir, normalize_name

Recipe = Dict[str, object]

DEFAULT_RECIPES: List[Recipe] = [
    {
        "name": "Scrambled Eggs",
        "ingredients": {"eggs": 2, "butter": 1, "salt": 1},
        "tags": ["vegetarian", "quick"],
    },
    {
        "name": "Garlic Butter Pasta",
        "ingredients": {
            "pasta": 1,
            "butter": 2,
            "garlic": 3,
            "salt": 1,
            "parmesan": 1,
        },
        "tags": ["vegetarian"],
    },
    {
        "name": "Vegetable Stir Fry",
        "ingredients": {
            "rice": 1,
            "soy sauce": 2,
            "garlic": 2,
            "broccoli": 1,
            "carrot": 1,
            "onion": 1,
        },
        "tags": ["vegetarian", "vegan"],
    },
    {
        "name": "Tomato Soup",
        "ingredients": {
            "tomato": 4,
            "onion": 1,
            "garlic": 2,
            "butter": 1,
            "salt": 1,
        },
        "tags": ["vegetarian"],
    },
    {
        "name": "Grilled Cheese Sandwich",
        "ingredients": {"bread": 2, "cheese": 2, "butter": 1},
        "tags": ["vegetarian", "quick"],
    },
    {
        "name": "Pancakes",
        "ingredients": {"flour": 2, "eggs": 1, "milk": 1, "butter": 1, "sugar": 1},
        "tags": ["vegetarian"],
    },
    {
        "name": "Chicken Fried Rice",
        "ingredients": {
            "rice": 2,
            "chicken": 1,
            "eggs": 1,
            "soy sauce": 2,
            "onion": 1,
            "garlic": 1,
        },
        "tags": [],
    },
    {
        "name": "Caprese Salad",
        "ingredients": {"tomato": 2, "cheese": 1, "olive oil": 1, "salt": 1},
        "tags": ["vegetarian", "quick"],
    },
]


def _recipes_file() -> Path:
    return _data_dir() / "recipes.json"


def load_recipes() -> List[Recipe]:
    """Load recipes from disk, seeding the file with defaults on first run."""
    path = _recipes_file()
    if not path.exists():
        save_recipes(DEFAULT_RECIPES)
        return [dict(r) for r in DEFAULT_RECIPES]
    with open(path, "r") as f:
        return json.load(f)


def save_recipes(recipes: List[Recipe]) -> None:
    """Persist the recipe list to disk."""
    data_dir = _data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    with open(_recipes_file(), "w") as f:
        json.dump(recipes, f, indent=2)


def normalize_recipe_ingredients(recipe: Recipe) -> Dict[str, float]:
    """Return the recipe's ingredients with normalized (lowercased) names."""
    raw = recipe.get("ingredients", {})
    return {normalize_name(k): v for k, v in raw.items()}


def recipe_has_tag(recipe: Recipe, tag: str) -> bool:
    """Return True if the recipe is tagged with the given tag (case-insensitive)."""
    tags = recipe.get("tags", [])
    return tag.lower() in {str(t).lower() for t in tags}
