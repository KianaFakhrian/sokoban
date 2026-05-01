"""
Sokoban Search Environment
Fundamentals and Applications of Artificial Intelligence Course
University of Isfahan - Spring 2026

Course Instructor: Dr. Marzieh Hosseini
Teaching Assistants:
    - Marzieh Karami
    - Masih Roughani
    - Fatemeh Sayadzade

This project provides a Sokoban-style search environment for the Fundamentals of Artificial Intelligence course.
In this environment, the agent must push boxes onto target locations while navigating a grid-based map with walls and other constraints.

The main objective of the project is to implement and compare several classical search algorithms, including:

- Breadth-First Search (BFS)
- Iterative Deepening Search (IDS)
- Uniform-Cost Search (UCS)
- A* Search

Key Components:
- State: Represents the current game state, including the player position and the positions of all boxes
- SokobanGame: The main environment that parses the level, stores walls and targets, and generates successor states
- Search Algorithms: Implementation of uninformed and informed search methods for solving the puzzle

Environment Features:
- Grid-based map representation
- Static walls and target cells
- Multiple boxes that must be moved to goal positions
- Different action costs for moving and pushing
- Pygame-based visualization
- Performance tracking through expanded nodes
- Text-based level definition

Usage:
    from env.gui import SokobanGUI

        gui = SokobanGUI()
        gui.run()

This project is designed for educational purposes and helps students explore the differences between uninformed and informed search techniques in a constrained search space.
"""


#######################################################
#                DONT CHANGE THIS PART                #
#######################################################

PUSH_COST = 5
MOVE_COST = 1


class State:
    def __init__(self, player_pos, boxes):
        self.player = player_pos  # (x, y)
        self.boxes = frozenset(boxes)  # set of (x, y) immutable

    def get_boxes(self):
        return list(self.boxes)

    def get_player_pos(self):
        x, y = self.player
        return (x, y)

    def __eq__(self, other):
        return self.player == other.player and self.boxes == other.boxes

    def __hash__(self):
        return hash((self.player, self.boxes))

    def __repr__(self):
        return f"State(player={self.player}, boxes={self.boxes})"


class SokobanGame:
    def __init__(self, level_str):
        self.walls = set()
        self.targets = set()
        self.width = 0
        self.height = 0
        self.initial_state = None
        self.expanded_nodes = 0
        self.parse_level(level_str)

    def parse_level(self, level_str):
        lines = [line.rstrip() for line in level_str.split('\n') if line.strip() != '']
        self.height = len(lines)
        self.width = max(len(line) for line in lines)

        boxes = set()
        player = None

        for y, line in enumerate(lines):
            for x, ch in enumerate(line):
                pos = (x, y)
                if ch == '#':
                    self.walls.add(pos)
                elif ch == '@':
                    player = pos
                elif ch == '$':
                    boxes.add(pos)
                elif ch == '.':
                    self.targets.add(pos)
                elif ch == '*':
                    boxes.add(pos)
                    self.targets.add(pos)
                elif ch == '+':
                    player = pos
                    self.targets.add(pos)
                # space is empty
        self.initial_state = State(player, boxes)

    def reset_expanded_counter(self):
        self.expanded_nodes = 0

    def get_expanded_nodes_count(self):
        return self.expanded_nodes

    def is_wall(self, pos):
        return pos in self.walls

    def is_target(self, pos):
        return pos in self.targets

    def in_grid(self, pos):
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height

    def get_successors(self, state):
        """Return list of (action, next_state, cost)"""
        successors = []
        self.expanded_nodes += 1
        x, y = state.player
        directions = {
            'U': (0, -1),
            'D': (0, 1),
            'L': (-1, 0),
            'R': (1, 0)
        }
        for action, (dx, dy) in directions.items():
            new_pos = (x + dx, y + dy)
            if self.is_wall(new_pos) or not self.in_grid(new_pos):
                continue

            boxes = set(state.boxes)
            if new_pos in boxes:
                # push box
                new_box_pos = (new_pos[0] + dx, new_pos[1] + dy)
                if self.is_wall(new_box_pos) or new_box_pos in boxes or not self.in_grid(new_box_pos):
                    continue
                # valid push
                boxes.remove(new_pos)
                boxes.add(new_box_pos)
                cost = PUSH_COST  # pushing cost more than moving
                push_action = action.lower()
                successors.append((push_action, State(new_pos, boxes), cost))
            else:
                # just move
                cost = MOVE_COST
                successors.append((action, State(new_pos, boxes), cost))
        return successors

    def is_goal(self, state):
        return all(b in self.targets for b in state.boxes)

    def get_targets(self):
        return set(self.targets)

    def get_walls(self):
        return set(self.walls)

    def get_initial_state(self):
        return self.initial_state

    def get_grid_width(self):
        return self.width

    def get_grid_height(self):
        return self.height