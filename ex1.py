import search 
import random
import math
import itertools


ids = ["000000000", "000000000"]


class HarryPotterProblem(search.Problem):
    """This class implements a Harry Potter problem according to problem description."""

    def __init__(self, initial):
        """The constructor for the HarryPotterProblem class"""
        self.map = initial['map']
        self.grid_height = len(self.map)
        self.grid_width = len(self.map[0]) if self.map else 0

        # Initialize wizards
        self.wizards = initial['wizards']
        self.wizard_names = tuple(self.wizards.keys())
        self.initial_wizard_positions = tuple(
            self.wizards[name][0] for name in self.wizard_names
        )
        self.initial_wizard_lives = tuple(
            self.wizards[name][1] for name in self.wizard_names
        )

        # Map wizard names to indices for easy lookup
        self.wizard_indices = {name: idx for idx, name in enumerate(self.wizard_names)}

        # Initialize horcrux positions
        self.horcrux_positions = initial['horcruxes']
        self.initial_horcrux_positions = tuple(self.horcrux_positions)

        # Initialize death eater paths and indices
        self.death_eaters = initial['death_eaters']
        self.death_eater_names = tuple(self.death_eaters.keys())
        self.death_eater_paths = tuple(self.death_eaters[name] for name in self.death_eater_names)
        self.initial_death_eater_indices = tuple(0 for _ in self.death_eater_names)
        self.initial_death_eater_directions = tuple(1 for _ in self.death_eater_names)
        self.initial_death_eater_positions = tuple(
            path[0] for path in self.death_eater_paths
        )

        # Voldemort's position
        self.voldemort_position = self.find_voldemort()

        # Initial Voldemort status
        self.initial_voldemort_status = True  # Voldemort is alive at the start

        # Initial state
        self.initial_state = (
            self.initial_wizard_positions,
            self.initial_horcrux_positions,
            self.initial_wizard_lives,
            self.initial_death_eater_positions,
            self.initial_death_eater_indices,
            self.initial_death_eater_directions,
            self.initial_voldemort_status,
            False  # game_over flag
        )

        search.Problem.__init__(self, self.initial_state)


    def find_voldemort(self):
        for x, row in enumerate(self.map):
            for y, cell in enumerate(row):
                if cell == 'V':  # 'V' represents Voldemort
                    return (x, y)
        return None  # Voldemort not found

    def is_valid_position(self, x, y):
        return 0 <= x < self.grid_height and 0 <= y < self.grid_width

    def actions(self, state):
        """Return the valid actions that can be executed in the given state."""
        wizard_positions, horcrux_positions, wizard_lives, _, _, _, voldemort_alive, game_over = state
        if game_over:
            return []  # No actions possible if the game is over

        horcrux_positions_set = set(horcrux_positions)
        possible_actions = []

        # For each wizard, determine possible actions
        for idx, (position, lives) in enumerate(zip(wizard_positions, wizard_lives)):
            if lives <= 0:
                continue  # Skip dead wizards

            wizard_name = self.wizard_names[idx]
            x, y = position
            actions = []

            # Possible moves: Up, Down, Left, Right
            moves = {
                (x - 1, y),  # Up
                (x + 1, y),  # Down
                (x, y - 1),  # Left
                (x, y + 1)   # Right
            }

            for new_x, new_y in moves:
                if self.is_valid_position(new_x, new_y):
                    cell = self.map[new_x][new_y]
                    if cell != 'I':  # 'I' represents impassable tiles
                        actions.append(("move", wizard_name, (new_x, new_y)))

            # Wait action
            actions.append(("wait", wizard_name))

            # Special actions: Destroy horcrux, Attack Voldemort
            if position in horcrux_positions_set:
                # Use the initial index of the horcrux based on initial_horcrux_positions
                initial_idx = self.initial_horcrux_positions.index(position)
                actions.append(("destroy", wizard_name, initial_idx))

            if voldemort_alive and position == self.voldemort_position and not horcrux_positions and wizard_name == 'Harry Potter':
                actions.append(("kill", "Harry Potter"))

            possible_actions.append(actions)

        # Ensure each wizard has exactly one action per turn
        action_combinations = list(itertools.product(*possible_actions))
        return action_combinations

    def result(self, state, action):
        """Return the state that results from executing the given action in the given state."""
        wizard_positions, horcrux_positions, wizard_lives, death_eater_positions, death_eater_indices, death_eater_directions, voldemort_alive, _ = state

        # Convert to lists for mutability
        new_wizard_positions = list(wizard_positions)
        new_horcrux_positions = list(horcrux_positions)
        new_wizard_lives = list(wizard_lives)
        new_death_eater_positions = list(death_eater_positions)
        new_death_eater_indices = list(death_eater_indices)
        new_death_eater_directions = list(death_eater_directions)
        new_voldemort_alive = voldemort_alive
        game_over = False  # Initialize game_over flag

        # Update death eater positions
        for idx in range(len(self.death_eater_names)):
            path = self.death_eater_paths[idx]
            current_index = new_death_eater_indices[idx]
            direction = new_death_eater_directions[idx]
            actions_ = ["move"]
            chosen_action = random.choice(actions_)

            # if chosen_action == "move":
            next_index = current_index + direction

                # Reverse direction if at the ends of the path
            if next_index >= len(path):
                direction = -1
                next_index = current_index + direction * 1
            elif next_index < 0:
                direction = 1
                next_index = current_index + direction * 1

            next_position = path[next_index]
            if self.is_valid_position(*next_position):
                cell = self.map[next_position[0]][next_position[1]]
                if cell != 'I':
                    # Update death eater index, position, and direction
                    new_death_eater_indices[idx] = next_index
                    new_death_eater_positions[idx] = next_position
                    new_death_eater_directions[idx] = direction
            else:
                # Death eater waits (stays in place)
                pass

        # elif chosen_action == "wait":
        #     pass

        # Store whether the last horcrux was destroyed this turn
        last_horcrux_destroyed = False

        # horcrux_attempts maps the initial horcrux index to list of wizards attempting to destroy it
        horcrux_attempts = {}
        for atomic_action in action:
            action_type = atomic_action[0]
            wizard_name = atomic_action[1]
            wizard_idx = self.wizard_indices[wizard_name]
            current_life = new_wizard_lives[wizard_idx]
            if current_life <= 0:
                continue  # Skip dead wizards

            if action_type == "move":
                _, _, new_position = atomic_action
                new_x, new_y = new_position
                if self.is_valid_position(new_x, new_y):
                    cell = self.map[new_x][new_y]
                    if cell != 'I':
                        new_wizard_positions[wizard_idx] = new_position

            elif action_type == "destroy":
                # This is the initial horcrux index
                _, _, initial_horcrux_index = atomic_action
                horcrux_pos = self.initial_horcrux_positions[initial_horcrux_index]
                if new_wizard_positions[wizard_idx] == horcrux_pos:
                    if initial_horcrux_index in horcrux_attempts:
                        horcrux_attempts[initial_horcrux_index].append(wizard_idx)
                    else:
                        horcrux_attempts[initial_horcrux_index] = [wizard_idx]

            elif action_type == "wait":
                pass

            elif action_type == "kill":
                if wizard_name == "Harry Potter" and not new_horcrux_positions and new_wizard_positions[wizard_idx] == self.voldemort_position:
                    new_voldemort_alive = False

        # Determine which horcruxes to remove based on attempts
        horcrux_indices_to_remove = []
        for initial_horcrux_index in horcrux_attempts.keys():
            if 0 <= initial_horcrux_index < len(self.initial_horcrux_positions):
                # Find the current index of this horcrux
                horcrux_pos = self.initial_horcrux_positions[initial_horcrux_index]
                if horcrux_pos in new_horcrux_positions:
                    current_index = new_horcrux_positions.index(horcrux_pos)
                    horcrux_indices_to_remove.append(current_index)

        horcrux_indices_to_remove.sort(reverse=True)
        for idx_to_remove in horcrux_indices_to_remove:
            del new_horcrux_positions[idx_to_remove]

        if len(new_horcrux_positions) == 0 and horcrux_indices_to_remove:
            last_horcrux_destroyed = True

        # Wizards lose lives if ending on death eater positions
        for idx, wizard_position in enumerate(new_wizard_positions):
            current_life = new_wizard_lives[idx]
            if current_life <= 0:
                continue
            if wizard_position in new_death_eater_positions:
                new_wizard_lives[idx] -= 1
                if new_wizard_lives[idx] <= 0:
                    game_over = True
                    break

        # Check for Voldemort interactions
        for wizard_idx, wizard_position in enumerate(new_wizard_positions):
            current_life = new_wizard_lives[wizard_idx]
            if current_life <= 0:
                continue
            if wizard_position == self.voldemort_position:
                if new_voldemort_alive:
                    if new_horcrux_positions:
                        # Horcruxes remain, wizard dies
                        new_wizard_lives[wizard_idx] = 0
                        game_over = True
                        break
                    else:
                        # Horcruxes destroyed
                        if self.wizard_names[wizard_idx] == 'Harry Potter':
                            if last_horcrux_destroyed:
                                new_wizard_lives[wizard_idx] = 0
                                game_over = True
                                break
                            else:
                                # Harry can survive and defeat Voldemort
                                pass
                        else:
                            # Other wizards die after horcruxes destroyed if they meet Voldemort
                            new_wizard_lives[wizard_idx] = 0
                            game_over = True
                            break
                else:
                    # Voldemort already defeated; no effect
                    pass

        # If any wizard's life <= 0 or Voldemort in a horcrux position or no Harry Potter alive -> game over
        if any(life <= 0 for life in new_wizard_lives) or self.voldemort_position in new_horcrux_positions or not any(name == 'Harry Potter' for name in self.wizard_names):
            game_over = True

        new_state = (
            tuple(new_wizard_positions),
            tuple(new_horcrux_positions),
            tuple(new_wizard_lives),
            tuple(new_death_eater_positions),
            tuple(new_death_eater_indices),
            tuple(new_death_eater_directions),
            new_voldemort_alive,
            game_over
        )

        return new_state

    def goal_test(self, state):
        """Return True if the state is a goal state."""
        _, horcrux_positions, wizards_lives, _, _, _, voldemort_alive, game_over = state
        
        if game_over:
            return False  # Cannot achieve goal if the game is over

        horcruxes_destroyed = len(horcrux_positions) == 0
        voldemort_defeated = not voldemort_alive
        win = horcruxes_destroyed and voldemort_defeated
        return win

    def h(self, node):
        """
        Heuristic function for A* search.
        """
        state = node.state
        wizard_positions, horcrux_positions, wizard_lives, _, _, _, voldemort_alive, game_over = state

        if game_over:
            return float('inf')

        if self.voldemort_position in horcrux_positions:
            return float('inf')

        if any(wizard_position == self.voldemort_position for wizard_position in wizard_positions) and voldemort_alive and horcrux_positions:
            return float('inf')

        if not horcrux_positions and not voldemort_alive:
            return 0

        horcruxes_alive = horcrux_positions
        total_distance = 0
        harry_index = self.wizard_indices.get('Harry Potter')

        for wizard_index, wizard_position in enumerate(wizard_positions):
            if wizard_lives[wizard_index] <= 0:
                continue

            if wizard_index == harry_index and len(wizard_positions) > 1:
                total_distance += 0.5 * sum(
                    self.manhattan_distance(wizard_position, horcrux) /
                    (self.manhattan_distance(horcrux, self.voldemort_position) + 1)
                    for horcrux in horcruxes_alive
                ) + 0.5 * self.manhattan_distance(wizard_position, self.voldemort_position)

            elif wizard_index == harry_index:
                total_distance += sum(
                    self.manhattan_distance(wizard_position, horcrux) *
                    self.manhattan_distance(horcrux, self.voldemort_position) /
                    (1 + len(wizard_positions) * len(horcruxes_alive))
                    for horcrux in horcruxes_alive
                )


            else:
                total_distance += sum(
                    self.manhattan_distance(wizard_position, horcrux) *
                    self.manhattan_distance(horcrux, self.voldemort_position) /
                    (1 + self.manhattan_distance(wizard_position, horcrux)) /
                    (1 + len(wizard_positions) * len(horcruxes_alive))
                    for horcrux in horcruxes_alive
                )

        total_distance += len(horcrux_positions)
        voldemort_incentive = 1 if not voldemort_alive else 0

        return total_distance + 1 - voldemort_incentive

    def manhattan_distance(self, pos1, pos2):
        """Calculates the Manhattan distance between two positions."""
        x1, y1 = pos1
        x2, y2 = pos2
        return abs(x1 - x2) + abs(y1 - y2)


def create_harrypotter_problem(game):
    return HarryPotterProblem(game)
