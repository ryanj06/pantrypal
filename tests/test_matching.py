from pantrypal.matching import match_recipe, shopping_list, suggest_recipes


def test_match_recipe_fully_makeable():
    recipe = {"name": "Toast", "ingredients": {"bread": 2, "butter": 1}}
    pantry = {"bread": 4, "butter": 2}
    match = match_recipe(recipe, pantry)
    assert match.is_makeable
    assert match.match_ratio == 1.0


def test_match_recipe_missing_ingredient():
    recipe = {"name": "Pancakes", "ingredients": {"flour": 2, "eggs": 1}}
    pantry = {"eggs": 3}
    match = match_recipe(recipe, pantry)
    assert not match.is_makeable
    assert "flour" in match.missing
    assert "eggs" in match.have


def test_match_recipe_insufficient_quantity():
    recipe = {"name": "Pasta", "ingredients": {"butter": 2, "pasta": 1}}
    pantry = {"butter": 1, "pasta": 1}
    match = match_recipe(recipe, pantry)
    assert "butter" in match.insufficient
    assert match.insufficient["butter"] == (1, 2)


def test_suggest_recipes_orders_makeable_first():
    recipes = [
        {"name": "A", "ingredients": {"x": 1, "y": 1}},
        {"name": "B", "ingredients": {"x": 1}},
    ]
    pantry = {"x": 1}
    matches = suggest_recipes(recipes, pantry, limit=2)
    assert matches[0].name == "B"
    assert matches[0].is_makeable


def test_shopping_list_aggregates_missing_and_insufficient():
    recipes = [
        {"name": "A", "ingredients": {"flour": 2, "butter": 1}},
        {"name": "B", "ingredients": {"flour": 1, "eggs": 1}},
    ]
    pantry = {"butter": 0.5, "eggs": 1}
    matches = suggest_recipes(recipes, pantry, limit=2)
    needs = shopping_list(matches)
    assert needs["flour"] == 3
    assert needs["butter"] == 0.5
    assert "eggs" not in needs
