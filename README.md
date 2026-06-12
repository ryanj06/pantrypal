# PantryPal

PantryPal is a command-line pantry tracker and meal planner. Keep a running
inventory of what's in your kitchen, and let PantryPal suggest recipes you
can make right now (or are close to being able to make), automatically
generating a shopping list for whatever's missing.

## Usage

Install with `uv`:

```bash
uv add "git+https://github.com/<your-username>/pantrypal.git"
```

### Managing your pantry

Add items to your pantry:

```bash
pantry add eggs 12
pantry add butter 1
pantry add garlic 5
```

Remove items (omit the quantity to remove the item entirely):

```bash
pantry remove eggs 2
pantry remove butter
```

List everything currently in your pantry:

```bash
pantry list
```

### Getting recipe suggestions

See which recipes you can make (or almost make) with what you have:

```bash
pantry suggest
```

This prints recipes ranked by how well they match your pantry, marking
fully makeable recipes as "Ready to make!" and showing missing or
insufficient ingredients for the rest.

### Generating a shopping list

Get a combined shopping list of everything missing across the top
suggested recipes:

```bash
pantry shopping-list
```

Or generate a shopping list for one specific recipe:

```bash
pantry shopping-list --recipe "Garlic Butter Pasta"
```

### Managing recipes

List all known recipes:

```bash
pantry recipes
```

Add your own recipe (ingredients given as alternating name/quantity pairs):

```bash
pantry add-recipe "Avocado Toast" bread 2 avocado 1 salt 1
```

PantryPal ships with a set of default recipes and stores your pantry and
recipe data in `~/.pantrypal/` (override with the `PANTRYPAL_HOME`
environment variable).
