"""Command-line interface for PantryPal."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from pantrypal.matching import shopping_list, suggest_recipes
from pantrypal.recipes import load_recipes, save_recipes
from pantrypal.storage import load_pantry, normalize_name, save_pantry


def cmd_pantry_add(args: argparse.Namespace) -> int:
    pantry = load_pantry()
    name = normalize_name(args.name)
    pantry[name] = pantry.get(name, 0) + args.quantity
    save_pantry(pantry)
    print(f"Added {args.quantity} {name} (now have {pantry[name]}).")
    return 0


def cmd_pantry_remove(args: argparse.Namespace) -> int:
    pantry = load_pantry()
    name = normalize_name(args.name)
    if name not in pantry:
        print(f"'{name}' is not in your pantry.")
        return 1

    if args.quantity is None or args.quantity >= pantry[name]:
        del pantry[name]
        print(f"Removed all of '{name}' from your pantry.")
    else:
        pantry[name] -= args.quantity
        print(f"Removed {args.quantity} {name} (now have {pantry[name]}).")

    save_pantry(pantry)
    return 0


def cmd_pantry_list(args: argparse.Namespace) -> int:
    pantry = load_pantry()
    if not pantry:
        print("Your pantry is empty. Add items with `pantry add <item> <qty>`.")
        return 0

    print("Your pantry:")
    for name, qty in sorted(pantry.items()):
        print(f"  {name}: {qty}")
    return 0


def cmd_meal_suggest(args: argparse.Namespace) -> int:
    pantry = load_pantry()
    recipes = load_recipes()
    matches = suggest_recipes(recipes, pantry, limit=args.limit)

    if not matches:
        print("No recipes found.")
        return 0

    for match in matches:
        status = "Ready to make!" if match.is_makeable else f"{match.match_ratio:.0%} match"
        print(f"\n{match.name} ({status})")

        if match.missing:
            missing_str = ", ".join(
                f"{ingredient} (need {qty})" for ingredient, qty in sorted(match.missing.items())
            )
            print(f"  Missing: {missing_str}")

        if match.insufficient:
            insuff_str = ", ".join(
                f"{ingredient} (have {have}, need {need})"
                for ingredient, (have, need) in sorted(match.insufficient.items())
            )
            print(f"  Not enough: {insuff_str}")

    return 0


def cmd_meal_shopping_list(args: argparse.Namespace) -> int:
    pantry = load_pantry()
    recipes = load_recipes()

    if args.recipe:
        target = [r for r in recipes if str(r["name"]).lower() == args.recipe.lower()]
        if not target:
            print(f"No recipe named '{args.recipe}' found.")
            return 1
        matches = suggest_recipes(target, pantry, limit=1)
    else:
        matches = suggest_recipes(recipes, pantry, limit=args.limit)

    needs = shopping_list(matches)
    if not needs:
        print("Nothing needed — you can make all of these with what you have!")
        return 0

    print("Shopping list:")
    for ingredient, qty in sorted(needs.items()):
        print(f"  {ingredient}: {qty}")
    return 0


def cmd_recipe_list(args: argparse.Namespace) -> int:
    recipes = load_recipes()
    for recipe in recipes:
        ingredients = ", ".join(
            f"{name} ({qty})" for name, qty in recipe["ingredients"].items()
        )
        print(f"{recipe['name']}: {ingredients}")
    return 0


def cmd_recipe_add(args: argparse.Namespace) -> int:
    if len(args.ingredients) % 2 != 0:
        print("Ingredients must be given as pairs: <name> <quantity> ...")
        return 1

    ingredients = {}
    for i in range(0, len(args.ingredients), 2):
        name = normalize_name(args.ingredients[i])
        try:
            qty = float(args.ingredients[i + 1])
        except ValueError:
            print(f"Invalid quantity '{args.ingredients[i + 1]}' for '{name}'.")
            return 1
        ingredients[name] = qty

    recipes = load_recipes()
    recipes.append({"name": args.name, "ingredients": ingredients})
    save_recipes(recipes)
    print(f"Added recipe '{args.name}' with {len(ingredients)} ingredients.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pantry",
        description="Track your pantry inventory and get recipe suggestions.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # pantry add/remove/list
    p_add = subparsers.add_parser("add", help="Add an item to your pantry")
    p_add.add_argument("name", help="Ingredient name")
    p_add.add_argument("quantity", type=float, help="Quantity to add")
    p_add.set_defaults(func=cmd_pantry_add)

    p_remove = subparsers.add_parser("remove", help="Remove an item from your pantry")
    p_remove.add_argument("name", help="Ingredient name")
    p_remove.add_argument(
        "quantity",
        type=float,
        nargs="?",
        default=None,
        help="Quantity to remove (omit to remove all)",
    )
    p_remove.set_defaults(func=cmd_pantry_remove)

    p_list = subparsers.add_parser("list", help="List items in your pantry")
    p_list.set_defaults(func=cmd_pantry_list)

    # meal suggest / shopping-list
    p_suggest = subparsers.add_parser(
        "suggest", help="Suggest recipes based on your pantry contents"
    )
    p_suggest.add_argument(
        "--limit", type=int, default=5, help="Max number of recipes to show (default: 5)"
    )
    p_suggest.set_defaults(func=cmd_meal_suggest)

    p_shopping = subparsers.add_parser(
        "shopping-list", help="Generate a shopping list of missing ingredients"
    )
    p_shopping.add_argument(
        "--recipe", help="Generate a shopping list for a specific recipe by name"
    )
    p_shopping.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Number of suggested recipes to base the list on (default: 5)",
    )
    p_shopping.set_defaults(func=cmd_meal_shopping_list)

    # recipe management
    p_recipe_list = subparsers.add_parser("recipes", help="List all known recipes")
    p_recipe_list.set_defaults(func=cmd_recipe_list)

    p_recipe_add = subparsers.add_parser("add-recipe", help="Add a new recipe")
    p_recipe_add.add_argument("name", help="Recipe name")
    p_recipe_add.add_argument(
        "ingredients",
        nargs="+",
        help="Alternating ingredient name and quantity pairs, e.g. eggs 2 milk 1",
    )
    p_recipe_add.set_defaults(func=cmd_recipe_add)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
