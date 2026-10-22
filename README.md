# Harry Potter Horcrux Search

Homework 1 for an Intro to AI course: **deterministic search**. It models a Harry Potter grid world as a search problem and solves it with A* and a custom heuristic.

The full assignment is in [`HW1.pdf`](HW1.pdf).

## The problem

The map is a grid of cells:

| Cell | Meaning |
|------|---------|
| `P` | Passable. Wizards, death eaters and horcruxes can be here. |
| `I` | Impassable. |
| `V` | Voldemort. Stepping here before every horcrux is destroyed kills the wizard. |

You control one or more wizards, including Harry Potter. The goal is to destroy every horcrux and then have Harry kill Voldemort, in as few turns as possible and without any wizard dying.

- **Actions.** Each wizard takes exactly one atomic action per turn: `("move", wizard, (r, c))`, `("destroy", wizard, horcrux_index)`, `("wait", wizard)` or `("kill", "Harry Potter")`. A full action is a tuple with one atomic action per wizard.
- **Death eaters** patrol fixed paths back and forth (A→B→C→B→A…). A wizard that ends a turn on a death eater's tile loses a life. At 0 lives the wizard dies and the game is lost.
- **Voldemort** can only be killed by Harry, and only after all horcruxes are destroyed. If Harry steps onto Voldemort's tile on the same turn the last horcrux is destroyed, Harry still dies.

## Solution (`ex1.py`)

`HarryPotterProblem` extends `search.Problem`:

- **State** is a hashable tuple: wizard positions, remaining horcruxes, wizard lives, death eater positions, path indices and directions, whether Voldemort is alive, and a game-over flag.
- **`actions`** builds each wizard's legal moves (4-neighbourhood, no `I` tiles), waits, destroys and kills, then takes the Cartesian product over all wizards.
- **`result`** advances the death eaters along their paths, applies wizard actions, removes destroyed horcruxes, and then checks for life loss and encounters with Voldemort.
- **`goal_test`**: all horcruxes are destroyed, Voldemort is dead, and the game is not over.
- **`h`** is a Manhattan-distance heuristic. It weighs each wizard's distance to the remaining horcruxes against how close those horcruxes are to Voldemort, adds the number of remaining horcruxes, and returns `inf` for dead-end states (game over, or a wizard on Voldemort's tile too early).

## Project structure

| File | Description |
|------|-------------|
| `ex1.py` | The solution: problem model and heuristic |
| `search.py` | Search algorithms (BFS, DFS, UCS, A*, …) provided by the course |
| `utils.py` | Course-provided helper utilities |
| `problems.py` | Sample problem instances |
| `check.py` | Runs A* on every sample problem with a 60-second timeout |
| `HW1.pdf` | The assignment |

## Running

Requires Python 3. There are no external dependencies.

```bash
python check.py
```

Each line of output is `A* (solution_length, seconds, actions)`. `(-2, -2, None)` means the problem timed out.

### Results on the sample problems

| Problem | Turns | Time |
|---------|-------|------|
| 1 | 10 | < 0.01 s |
| 2 | 10 | < 0.01 s |
| 3 | 12 | < 0.01 s |
| 4 | 16 | < 0.01 s |
