import pygame
import sys
import time
import os
from env.levels import levels
from env.sokoban import SokobanGame, PUSH_COST, MOVE_COST
from search import bfs_solve, ids_solve, ucs_solve, astar_solve

#######################################################
#                DONT CHANGE THIS PART                #
#######################################################

# Constantss
TILE_SIZE = 50
BUTTON_COLOR = (100, 200, 100)
BUTTON_HOVER = (150, 250, 150)
TEXT_COLOR = (0, 0, 0)
BUTTON_RADIUS = 9

class SokobanGUI:
    def __init__(self):
        pygame.init()
        self.screen = None
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 26)
        self.small_font = pygame.font.Font(None, 23)

        self.levels = levels
        self.level_names = list(levels.keys())
        self.current_level_idx = 0
        self.game = None
        self.current_state = None
        self.solution_path = []
        self.step_index = 0
        self.playing = False
        self.play_timer = 0
        self.status_msg = ""
        self.algorithm_time = 0
        self.algorithm_expanded_nodes = 0
        self.algorithm_cost = 0

        self.images = {}
        self.level_btn_images = {}
        self.background = None
        self.load_images()
        self.load_level(self.current_level_idx)

    def load_images(self):
        img_dir = "env/img"
        image_files = {
            '#': 'wall1.png',
            ' ': 'space1.png',
            '$': 'stone1.png',
            '.': 'switch1.png',
            '@': 'ares1.png',
            '+': 'ares_on_switch1.png',
            '*': 'stone_on_switch1.png',
        }

        for key, filename in image_files.items():
            path = os.path.join(img_dir, filename)
            try:
                img = pygame.image.load(path)
                img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
                self.images[key] = img
            except pygame.error as e:
                print(f"Warning: Could not load image {path}: {e}")
                surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
                if key == '#':
                    surf.fill((50, 50, 50))
                elif key == ' ':
                    surf.fill((240, 240, 240))
                elif key == '$':
                    surf.fill((139, 69, 19))
                elif key == '.':
                    surf.fill((255, 200, 200))
                elif key == '@':
                    surf.fill((0, 100, 200))
                elif key == '+':
                    surf.fill((0, 200, 100))
                elif key == '*':
                    surf.fill((200, 150, 50))
                self.images[key] = surf

    def load_level(self, idx):
        level_str = self.levels[self.level_names[idx]]
        self.game = SokobanGame(level_str)
        self.current_state = self.game.get_initial_state()
        self.solution_path = []
        self.step_index = 0
        self.playing = False
        self.algorithm_expanded_nodes = 0
        self.algorithm_cost = 0
        self.status_msg = f"Level: {self.level_names[idx]}"
        self._resize_screen()

    def _resize_screen(self):
        panel_height = 100
        panel_width = 580
        width = max(self.game.width * TILE_SIZE, panel_width)
        height = self.game.height * TILE_SIZE + panel_height
        self.screen = pygame.display.set_mode((width, height))

        bg_path = os.path.join('env/img', "background.png")
        try:
            self.background = pygame.image.load(bg_path).convert()
        except FileNotFoundError as error:
            print('pic dosent exist')
            self.background = None
        except pygame.error as e:
            print(f"Warning: Could not load background image {bg_path}: {e}")
            self.background = None
        if self.background:
            self.background = pygame.transform.scale(self.background, (width, height))
        else:
            self.background = None

        self.level_btn_images = {
            'prev_normal': None,
            'prev_hover': None,
            'next_normal': None,
            'next_hover': None,
        }
        btn_files = {
            'prev_normal': 'button.png',
            'prev_hover': 'button_hover.png',
            'next_normal': 'button.png',
            'next_hover': 'button_hover.png',
        }

        for key, filename in btn_files.items():
            path = os.path.join('env/img', filename)
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (40, 25))
                self.level_btn_images[key] = img
            except pygame.error as e:
                print(f"Warning: Could not load button image {path}: {e}")

        pygame.display.set_caption("Sokoban")

    def draw_grid(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((255, 255, 255))
        for y in range(self.game.height):
            for x in range(self.game.width):
                pos = (x, y)
                if pos in self.game.walls:
                    key = '#'
                elif pos in self.current_state.boxes:
                    if pos in self.game.targets:
                        key = '*'
                    else:
                        key = '$'
                elif pos == self.current_state.player:
                    if pos in self.game.targets:
                        key = '+'
                    else:
                        key = '@'
                elif pos in self.game.targets:
                    key = '.'
                else:
                    key = ' '

                img = self.images.get(key)
                if img:
                    self.screen.blit(img, (x * TILE_SIZE, y * TILE_SIZE))

    def draw_panel(self):
        panel_y = self.game.height * TILE_SIZE
        panel_rect = pygame.Rect(0, panel_y, self.screen.get_width(), 100)

        s = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        s.fill((0, 0, 0, 50))
        self.screen.blit(s, (0, panel_y))

        pygame.draw.line(self.screen, (255, 255, 255), (0, panel_y), (self.screen.get_width(), panel_y), 1)

        # Status text
        text_surf = self.font.render(self.status_msg, True, TEXT_COLOR)
        self.screen.blit(text_surf, (10, panel_y + 5))

        # Algorithm buttons
        btn_y = panel_y + 30
        btn_w = 80
        btn_h = 30
        gap = 10
        x = 10
        buttons = [
            ("BFS", self.run_bfs),
            ("IDS", self.run_ids),
            ("UCS", self.run_ucs),
            ("A*", self.run_astar),
        ]
        for label, action in buttons:
            btn_rect = pygame.Rect(x, btn_y, btn_w, btn_h)
            mouse_pos = pygame.mouse.get_pos()
            hover = btn_rect.collidepoint(mouse_pos)
            color = BUTTON_HOVER if hover else BUTTON_COLOR
            pygame.draw.rect(self.screen, color, btn_rect, border_radius=BUTTON_RADIUS)
            pygame.draw.rect(self.screen, (0, 0, 0), btn_rect, width=2, border_radius=BUTTON_RADIUS)
            text = self.small_font.render(label, True, TEXT_COLOR)
            text_rect = text.get_rect(center=btn_rect.center)
            self.screen.blit(text, text_rect)
            attr_name = f"btn_{label.replace('*', 'star')}_rect"
            setattr(self, attr_name, btn_rect)
            x += btn_w + gap

        # Play/Pause/Step buttons
        play_btn = pygame.Rect(x, btn_y, 60, btn_h)
        pygame.draw.rect(self.screen, (100,100,200), play_btn, border_radius=BUTTON_RADIUS)
        pygame.draw.rect(self.screen, (0,0,0), play_btn, 2, border_radius=BUTTON_RADIUS)
        self.screen.blit(self.small_font.render("Play", True, TEXT_COLOR), (x+15, btn_y+8))
        self.btn_play_rect = play_btn
        x += 70

        step_btn = pygame.Rect(x, btn_y, 60, btn_h)
        pygame.draw.rect(self.screen, (200,200,100), step_btn, border_radius=BUTTON_RADIUS)
        pygame.draw.rect(self.screen, (0,0,0), step_btn, 2, border_radius=BUTTON_RADIUS)
        self.screen.blit(self.small_font.render("Step", True, TEXT_COLOR), (x+15, btn_y+8))
        self.btn_step_rect = step_btn
        x += 70

        reset_btn = pygame.Rect(x, btn_y, 60, btn_h)
        pygame.draw.rect(self.screen, (200,100,100), reset_btn, border_radius=BUTTON_RADIUS)
        pygame.draw.rect(self.screen, (0,0,0), reset_btn, 2, border_radius=BUTTON_RADIUS)
        self.screen.blit(self.small_font.render("Reset", True, TEXT_COLOR), (x+10, btn_y+8))
        self.btn_reset_rect = reset_btn

        #Choose level buttons
        level_y = panel_y + 65
        base_x = 10

        mouse_pos = pygame.mouse.get_pos()

        prev_rect = pygame.Rect(base_x, level_y, 40, 25)
        hover_prev = prev_rect.collidepoint(mouse_pos)

        if self.level_btn_images['prev_normal'] and self.level_btn_images['prev_hover']:
            bg_img = self.level_btn_images['prev_hover'] if hover_prev else self.level_btn_images['prev_normal']
            self.screen.blit(bg_img, prev_rect)
        else:
            color = (180, 180, 180) if hover_prev else (150, 150, 150)
            pygame.draw.rect(self.screen, color, prev_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), prev_rect, 2)

        prev_text = self.small_font.render("<", True, TEXT_COLOR)
        prev_text_rect = prev_text.get_rect(center=prev_rect.center)
        self.screen.blit(prev_text, prev_text_rect)

        self.btn_prev_rect = prev_rect

        text_x = prev_rect.right + 10
        level_text = self.small_font.render(self.level_names[self.current_level_idx], True, TEXT_COLOR)
        level_text_rect = level_text.get_rect(midleft=(text_x, level_y + 14))
        self.screen.blit(level_text, level_text_rect)

        next_rect = pygame.Rect(level_text_rect.right + 10, level_y, 40, 25)
        hover_next = next_rect.collidepoint(mouse_pos)

        if self.level_btn_images['next_normal'] and self.level_btn_images['next_hover']:
            bg_img = self.level_btn_images['next_hover'] if hover_next else self.level_btn_images['next_normal']
            self.screen.blit(bg_img, next_rect)
        else:
            color = (180, 180, 180) if hover_next else (150, 150, 150)
            pygame.draw.rect(self.screen, color, next_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), next_rect, 2)

        next_text = self.small_font.render(">", True, TEXT_COLOR)
        next_text_rect = next_text.get_rect(center=next_rect.center)
        self.screen.blit(next_text, next_text_rect)

        self.btn_next_rect = next_rect

        # Time display
        if self.algorithm_time:
            time_text = self.small_font.render(f"Time: {self.algorithm_time:.2f}s", True, TEXT_COLOR)
            self.screen.blit(time_text, (self.screen.get_width()-150, panel_y+5))

    def cal_cost(self, path):
        cost = 0
        for action in path:
            if action.islower():
                cost+= PUSH_COST
            else:
                cost+= MOVE_COST
        return cost

    def run_algorithm(self, algo_func, *args):
        self.status_msg = "Searching..."
        self.draw_all()
        pygame.display.flip()
        self.game.reset_expanded_counter()
        start_time = time.time()
        path = algo_func(*args)
        self.algorithm_time = time.time() - start_time
        self.algorithm_expanded_nodes = self.game.get_expanded_nodes_count()
        if path is None:
            self.status_msg = f"No solution. Expanded nodes: {self.algorithm_expanded_nodes}"
            self.solution_path = []
        else:
            self.algorithm_cost = self.cal_cost(path)
            self.status_msg = f"Length: {len(path)}, Expanded nodes: {self.algorithm_expanded_nodes}, Cost: {self.algorithm_cost}"
            self.solution_path = path
            self.step_index = 0
            self.current_state = self.game.get_initial_state()
        self.playing = False

    def run_bfs(self):
        self.run_algorithm(bfs_solve, self.game)

    def run_ids(self):
        self.run_algorithm(ids_solve, self.game)

    def run_ucs(self):
        self.run_algorithm(ucs_solve, self.game)

    def run_astar(self):
        self.run_algorithm(astar_solve, self.game)

    def step_solution(self):
        if self.step_index < len(self.solution_path):
            action = self.solution_path[self.step_index]
            for a, ns, _ in self.game.get_successors(self.current_state):
                if a == action:
                    self.current_state = ns
                    break
            self.step_index += 1
            if self.step_index >= len(self.solution_path):
                self.playing = False
                if self.game.is_goal(self.current_state):
                    self.status_msg = "Puzzle solved!"
            return True
        return False

    def reset_to_start(self):
        self.current_state = self.game.get_initial_state()
        self.step_index = 0
        self.playing = False

    def draw_all(self):
        self.draw_grid()
        self.draw_panel()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if hasattr(self, 'btn_BFS_rect') and self.btn_BFS_rect.collidepoint(pos):
                    self.run_bfs()
                elif hasattr(self, 'btn_IDS_rect') and self.btn_IDS_rect.collidepoint(pos):
                    self.run_ids()
                elif hasattr(self, 'btn_UCS_rect') and self.btn_UCS_rect.collidepoint(pos):
                    self.run_ucs()
                elif hasattr(self, 'btn_Astar_rect') and self.btn_Astar_rect.collidepoint(pos):
                    self.run_astar()
                elif hasattr(self, 'btn_play_rect') and self.btn_play_rect.collidepoint(pos):
                    if self.solution_path:
                        self.playing = True
                elif hasattr(self, 'btn_step_rect') and self.btn_step_rect.collidepoint(pos):
                    if self.solution_path:
                        self.step_solution()
                elif hasattr(self, 'btn_reset_rect') and self.btn_reset_rect.collidepoint(pos):
                    self.reset_to_start()
                elif hasattr(self, 'btn_prev_rect') and self.btn_prev_rect.collidepoint(pos):
                    self.current_level_idx = (self.current_level_idx - 1) % len(self.level_names)
                    self.load_level(self.current_level_idx)
                elif hasattr(self, 'btn_next_rect') and self.btn_next_rect.collidepoint(pos):
                    self.current_level_idx = (self.current_level_idx + 1) % len(self.level_names)
                    self.load_level(self.current_level_idx)
        return True

    def update(self):
        if self.playing and self.solution_path:
            now = pygame.time.get_ticks()
            if now - self.play_timer > 500:
                self.play_timer = now
                if not self.step_solution():
                    self.playing = False

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw_all()
            pygame.display.flip()
            self.clock.tick(30)
        pygame.quit()
        sys.exit()