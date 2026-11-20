"""AI Game Jam: scrolling road game with steering and obstacles."""

import json
import math
import random
from pathlib import Path

import pygame

WIDTH, HEIGHT = 960, 640
FPS = 60

GRASS = (69, 135, 82)
ROAD = (55, 55, 60)
LANE = (235, 235, 235)
RAIL = (190, 190, 205)
RAIL_POST = (120, 120, 135)
CAR = (220, 70, 70)
RIVAL = (70, 160, 255)
TEXT = (255, 255, 255)
OBSTACLE = (255, 165, 0)
BEAR_BODY = (120, 84, 52)
BEAR_BELLY = (170, 132, 92)
BEAR_EAR = (94, 62, 36)
BEAR_NOSE = (35, 28, 24)
CRATE = (166, 112, 62)
CRATE_DARK = (120, 77, 39)
CRATE_LIGHT = (196, 140, 88)
LOG_BARK = (110, 82, 52)
LOG_RING = (178, 142, 96)
LOG_MOSS = (74, 120, 70)
SAPLING_TRUNK = (110, 82, 50)
SAPLING_LEAF_DARK = (38, 112, 56)
SAPLING_LEAF_LIGHT = (68, 152, 84)
TREE_TRUNK = (95, 65, 40)
TREE_LEAF_DARK = (34, 95, 48)
TREE_LEAF_LIGHT = (52, 128, 70)
DISCO_COLORS = [(255, 80, 120), (80, 240, 255), (250, 245, 90), (180, 110, 255)]
MENU_BG = (22, 22, 30)
MENU_PANEL = (36, 36, 48)
MENU_HIGHLIGHT = (82, 132, 255)
MAP_LABEL = (200, 210, 230)

PLAYER_Y = HEIGHT - 120
ROAD_WIDTH = 230
SECOND_ROAD_OFFSET = 300
SEGMENT_LENGTH = 80
MAX_TURN = 190
SAFE_START_DISTANCE = 1300
HIGHSCORE_FILE = Path("highscores.json")
STRAIGHT_ZONE_FIRST_START = 2600
STRAIGHT_ZONE_INTERVAL = 5200
STRAIGHT_ZONE_LENGTH = 1300
CONNECTOR_FIRST_START = 1800
CONNECTOR_INTERVAL = 3200
CONNECTOR_LENGTH = 500

VEHICLE_ORDER = ["motorbike", "rally_car", "bus"]
VEHICLE_PROFILES = {
    "motorbike": {
        "name": "Moottoripyora",
        "sprite": "bike",
        "width": 26,
        "height": 62,
        "base_speed": 5.2,
        "max_speed": 12.8,
        "min_speed": 2.3,
        "accel": 0.22,
        "brake": 0.26,
        "steer": 6.8,
        "jump": 26,
    },
    "rally_car": {
        "name": "Ralliauto",
        "sprite": "car",
        "width": 40,
        "height": 68,
        "base_speed": 5.0,
        "max_speed": 11.7,
        "min_speed": 2.0,
        "accel": 0.18,
        "brake": 0.24,
        "steer": 6.1,
        "jump": 26,
    },
    "bus": {
        "name": "Bussi",
        "sprite": "bus",
        "width": 52,
        "height": 96,
        "base_speed": 4.3,
        "max_speed": 9.5,
        "min_speed": 1.8,
        "accel": 0.14,
        "brake": 0.2,
        "steer": 4.5,
        "jump": 22,
    },
}
MAP_ORDER = ["argentina", "suomi", "ruotsi", "englanti"]
MAP_PROFILES = {
    "argentina": {
        "name": "Argentiina",
        "track": "Kaupunkikentta",
        "bg": (105, 108, 120),
        "scenery": "city",
    },
    "suomi": {
        "name": "Suomi",
        "track": "Metsakentta",
        "bg": GRASS,
        "scenery": "forest",
    },
    "ruotsi": {
        "name": "Ruotsi",
        "track": "Vesimaisemakentta",
        "bg": (90, 142, 168),
        "scenery": "water",
    },
    "englanti": {
        "name": "Englanti",
        "track": "Rantakentta",
        "bg": (212, 196, 148),
        "scenery": "beach",
    },
}


def in_straight_safe_zone(world_y):
    if world_y < STRAIGHT_ZONE_FIRST_START:
        return False
    phase = (world_y - STRAIGHT_ZONE_FIRST_START) % STRAIGHT_ZONE_INTERVAL
    return phase < STRAIGHT_ZONE_LENGTH


def in_connector_zone(world_y):
    if world_y < CONNECTOR_FIRST_START:
        return False
    phase = (world_y - CONNECTOR_FIRST_START) % CONNECTOR_INTERVAL
    return phase < CONNECTOR_LENGTH


class Road:
    def __init__(self):
        self.points = []
        self.turn_target = WIDTH // 2
        self.turn_frames = 0
        self._add_initial_points()

    def _add_initial_points(self):
        center = WIDTH // 2
        y = -SEGMENT_LENGTH
        for _ in range(70):
            self.points.append((y, center))
            y += SEGMENT_LENGTH

    def extend_if_needed(self, max_needed_y):
        while self.points[-1][0] < max_needed_y:
            prev_y, prev_center = self.points[-1]
            if in_straight_safe_zone(prev_y):
                self.points.append((prev_y + SEGMENT_LENGTH, prev_center))
                continue
            if self.turn_frames <= 0:
                self.turn_target = random.randint(220, WIDTH - 220)
                self.turn_frames = random.randint(5, 12)
            self.turn_frames -= 1
            shift = (self.turn_target - prev_center) * 0.18
            shift = max(-MAX_TURN, min(MAX_TURN, shift))
            next_center = int(prev_center + shift)
            next_center = max(180, min(WIDTH - 180, next_center))
            self.points.append((prev_y + SEGMENT_LENGTH, next_center))

    def center_at(self, world_y):
        for i in range(len(self.points) - 1):
            y1, x1 = self.points[i]
            y2, x2 = self.points[i + 1]
            if y1 <= world_y <= y2:
                t = 0.0 if y2 == y1 else (world_y - y1) / (y2 - y1)
                return x1 + (x2 - x1) * t
        return self.points[-1][1]

    def centers_at(self, world_y):
        center = self.center_at(world_y)
        left_center = max(140, center - SECOND_ROAD_OFFSET)
        return [center, left_center]

    def _draw_road_segment(self, screen, x1, y1, x2, y2):
        left1 = (x1 - ROAD_WIDTH // 2, y1)
        right1 = (x1 + ROAD_WIDTH // 2, y1)
        left2 = (x2 - ROAD_WIDTH // 2, y2)
        right2 = (x2 + ROAD_WIDTH // 2, y2)
        pygame.draw.polygon(screen, ROAD, (left1, right1, right2, left2))
        pygame.draw.line(screen, RAIL, left1, left2, 4)
        pygame.draw.line(screen, RAIL, right1, right2, 4)
        pygame.draw.line(screen, LANE, (x1, y1), (x2, y2), 4)

    def _draw_connector_segment(self, screen, main1, main2, left1, left2, y1, y2):
        polygon = (
            (left1 + ROAD_WIDTH // 2, y1),
            (main1 - ROAD_WIDTH // 2, y1),
            (main2 - ROAD_WIDTH // 2, y2),
            (left2 + ROAD_WIDTH // 2, y2),
        )
        pygame.draw.polygon(screen, ROAD, polygon)
        mid_x1 = (left1 + main1) // 2
        mid_x2 = (left2 + main2) // 2
        pygame.draw.line(screen, LANE, (mid_x1, y1), (mid_x2, y2), 3)

    def draw(self, screen, distance):
        visible_start = distance - 160
        visible_end = distance + PLAYER_Y + 220
        self.extend_if_needed(visible_end + 500)

        for i in range(len(self.points) - 1):
            y1, x1 = self.points[i]
            y2, x2 = self.points[i + 1]
            if y2 < visible_start or y1 > visible_end:
                continue

            sy1 = PLAYER_Y - (y1 - distance)
            sy2 = PLAYER_Y - (y2 - distance)
            main1 = x1
            main2 = x2
            left1 = max(140, x1 - SECOND_ROAD_OFFSET)
            left2 = max(140, x2 - SECOND_ROAD_OFFSET)
            self._draw_road_segment(screen, main1, sy1, main2, sy2)
            self._draw_road_segment(screen, left1, sy1, left2, sy2)
            if in_connector_zone((y1 + y2) * 0.5):
                self._draw_connector_segment(screen, main1, main2, left1, left2, sy1, sy2)

            if i % 2 == 0:
                pygame.draw.circle(screen, RAIL_POST, (int(main1 - ROAD_WIDTH // 2), int(sy1)), 4)
                pygame.draw.circle(screen, RAIL_POST, (int(main1 + ROAD_WIDTH // 2), int(sy1)), 4)
                pygame.draw.circle(screen, RAIL_POST, (int(left1 - ROAD_WIDTH // 2), int(sy1)), 4)
                pygame.draw.circle(screen, RAIL_POST, (int(left1 + ROAD_WIDTH // 2), int(sy1)), 4)


class Car:
    def __init__(self, vehicle_key):
        self.vehicle_key = vehicle_key
        self.set_vehicle(vehicle_key)

    def set_vehicle(self, vehicle_key):
        profile = VEHICLE_PROFILES[vehicle_key]
        self.vehicle_name = profile["name"]
        self.sprite = profile["sprite"]
        self.width = profile["width"]
        self.height = profile["height"]
        self.half_width = self.width // 2
        self.base_speed = profile["base_speed"]
        self.max_speed = profile["max_speed"]
        self.min_speed = profile["min_speed"]
        self.accel = profile["accel"]
        self.brake = profile["brake"]
        self.steer_strength = profile["steer"]
        self.jump_frames = profile["jump"]
        self.reset()

    def reset(self):
        self.x = WIDTH // 2
        self.speed = self.base_speed
        self.jump_timer = 0

    def update(self, keys):
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed += self.accel
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed -= self.brake
        self.speed = max(self.min_speed, min(self.max_speed, self.speed))

        steer = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            steer -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            steer += 1.0
        self.x += steer * self.steer_strength
        self.x = max(40, min(WIDTH - 40, self.x))
        if self.jump_timer > 0:
            self.jump_timer -= 1

    def try_jump(self):
        if self.jump_timer == 0:
            self.jump_timer = self.jump_frames

    def is_jumping(self):
        return self.jump_timer > 0

    def jump_height(self):
        if self.jump_timer == 0:
            return 0
        progress = 1.0 - (self.jump_timer / float(self.jump_frames))
        return max(0, int(math.sin(progress * math.pi) * 48))

    def draw(self, screen):
        jump = self.jump_height()
        draw_y = PLAYER_Y - jump
        car_rect = pygame.Rect(0, 0, self.width, self.height)
        car_rect.center = (int(self.x), draw_y)
        if jump > 0:
            shadow = pygame.Rect(0, 0, int(self.width * 1.1), max(10, int(self.width * 0.46)))
            shadow.center = (int(self.x), PLAYER_Y + 18)
            pygame.draw.ellipse(screen, (30, 30, 35), shadow)
        if self.sprite == "bus":
            draw_bus(screen, int(self.x), int(draw_y), self.width, self.height, CAR)
        elif self.sprite == "car":
            draw_rally_car(screen, int(self.x), int(draw_y), self.width, self.height, CAR)
        else:
            draw_bike(screen, int(self.x), int(draw_y), self.height, CAR)


class ComputerRider:
    def __init__(self, road):
        profile = VEHICLE_PROFILES["motorbike"]
        self.width = profile["width"]
        self.height = profile["height"]
        self.half_width = self.width // 2
        self.reset(road)

    def reset(self, road):
        self.distance = 380.0
        self.speed = 5.8
        centers = road.centers_at(self.distance)
        self.x = float(random.choice(centers))
        self.target_x = self.x
        self.switch_timer = 0
        self.crash_timer = 0

    def update(self, road, obstacles, player_distance):
        if self.distance < player_distance - 500:
            self.distance = player_distance + random.randint(320, 700)
            centers = road.centers_at(self.distance)
            self.x = float(random.choice(centers))
            self.target_x = self.x
            self.crash_timer = 0

        rel = self.distance - player_distance
        target_speed = 6.4 if rel < 240 else 5.6
        if self.crash_timer > 0:
            self.crash_timer -= 1
            target_speed = 2.8
        self.speed += (target_speed - self.speed) * 0.06
        self.speed = max(2.2, min(9.6, self.speed))
        self.distance += self.speed

        centers = road.centers_at(self.distance)
        nearest_center = min(centers, key=lambda c: abs(c - self.x))
        if self.switch_timer > 0:
            self.switch_timer -= 1
        if in_connector_zone(self.distance) and self.switch_timer == 0 and random.random() < 0.06:
            self.target_x = float(max(centers, key=lambda c: abs(c - nearest_center)))
            self.switch_timer = 44
        elif self.switch_timer == 0:
            self.target_x = float(nearest_center)

        self.x += (self.target_x - self.x) * 0.1
        left_limit, right_limit = road_side_limits(road, self.distance, self.x, self.half_width)
        self.x = max(left_limit, min(right_limit, self.x))

        if obstacles.hit_test_entity(self.x, self.distance, self.width, self.height):
            self.crash_timer = 40
            self.speed = 2.8

    def draw(self, screen, player_distance):
        screen_y = PLAYER_Y - int(self.distance - player_distance)
        if screen_y < -120 or screen_y > HEIGHT + 120:
            return
        draw_bike(screen, int(self.x), screen_y, self.height, RIVAL)


class ObstacleField:
    def __init__(self):
        self.obstacles = []
        self.last_spawn_y = SAFE_START_DISTANCE

    def reset(self):
        self.obstacles = []
        self.last_spawn_y = SAFE_START_DISTANCE

    def update(self, road, distance):
        spawn_until = distance + PLAYER_Y + 500
        while self.last_spawn_y < spawn_until:
            if in_straight_safe_zone(self.last_spawn_y) or in_connector_zone(self.last_spawn_y):
                self.last_spawn_y += random.randint(120, 180)
                continue
            centers = road.centers_at(self.last_spawn_y)
            center = random.choice(centers)
            half_road = ROAD_WIDTH // 2 - 24
            x = int(center + random.randint(-half_road, half_road))
            pick = random.random()
            if pick < 0.14:
                kind = "road_tree"
            elif pick < 0.5:
                kind = "bear"
            elif pick < 0.8:
                kind = "crate"
            elif pick < 0.92:
                kind = "log"
            else:
                kind = "small_tree"

            if kind == "road_tree":
                self.obstacles.append(
                    {
                        "x": int(center),
                        "y": self.last_spawn_y,
                        "w": ROAD_WIDTH - 34,
                        "h": 30,
                        "kind": kind,
                    }
                )
            elif kind == "small_tree":
                self.obstacles.append({"x": x, "y": self.last_spawn_y, "w": 30, "h": 28, "kind": kind})
            else:
                self.obstacles.append({"x": x, "y": self.last_spawn_y, "w": 34, "h": 34, "kind": kind})
            self.last_spawn_y += random.randint(140, 240)

        keep_from = distance - 140
        self.obstacles = [o for o in self.obstacles if o["y"] >= keep_from]

    def draw(self, screen, distance):
        for o in self.obstacles:
            sy = PLAYER_Y - (o["y"] - distance)
            if sy < -80 or sy > HEIGHT + 80:
                continue
            rect = pygame.Rect(0, 0, o["w"], o["h"])
            rect.center = (o["x"], int(sy))
            if o.get("kind") == "road_tree":
                self._draw_road_tree(screen, rect)
            elif o.get("kind") == "crate":
                self._draw_crate(screen, rect)
            elif o.get("kind") == "log":
                self._draw_log(screen, rect)
            elif o.get("kind") == "small_tree":
                self._draw_small_tree(screen, rect)
            else:
                self._draw_bear(screen, rect)

    def _draw_bear(self, screen, rect):
        body = pygame.Rect(rect.x + 1, rect.y + 10, rect.w - 2, rect.h - 10)
        pygame.draw.ellipse(screen, BEAR_BODY, body)
        head_center = (rect.centerx, rect.y + 12)
        pygame.draw.circle(screen, BEAR_BODY, head_center, 11)
        pygame.draw.circle(screen, BEAR_EAR, (head_center[0] - 8, head_center[1] - 7), 4)
        pygame.draw.circle(screen, BEAR_EAR, (head_center[0] + 8, head_center[1] - 7), 4)
        pygame.draw.ellipse(screen, BEAR_BELLY, (rect.x + 10, rect.y + 18, rect.w - 20, rect.h - 16))
        pygame.draw.ellipse(screen, BEAR_BELLY, (head_center[0] - 6, head_center[1] - 1, 12, 8))
        pygame.draw.circle(screen, BEAR_NOSE, (head_center[0], head_center[1] + 2), 2)

    def _draw_crate(self, screen, rect):
        pygame.draw.rect(screen, CRATE, rect, border_radius=4)
        pygame.draw.rect(screen, CRATE_DARK, rect, 3, border_radius=4)
        pygame.draw.line(screen, CRATE_LIGHT, (rect.x + 4, rect.y + 4), (rect.right - 4, rect.bottom - 4), 2)
        pygame.draw.line(screen, CRATE_LIGHT, (rect.right - 4, rect.y + 4), (rect.x + 4, rect.bottom - 4), 2)

    def _draw_log(self, screen, rect):
        log = pygame.Rect(rect.x - 2, rect.y + 10, rect.w + 4, rect.h - 14)
        pygame.draw.ellipse(screen, LOG_BARK, log)
        left_cap = pygame.Rect(log.x - 3, log.y + 3, 12, log.h - 6)
        right_cap = pygame.Rect(log.right - 9, log.y + 3, 12, log.h - 6)
        pygame.draw.ellipse(screen, LOG_RING, left_cap)
        pygame.draw.ellipse(screen, LOG_RING, right_cap)
        pygame.draw.ellipse(screen, LOG_MOSS, (log.x + 10, log.y + 2, log.w - 20, 6))

    def _draw_small_tree(self, screen, rect):
        trunk = pygame.Rect(rect.centerx - 3, rect.y + 12, 6, rect.h - 10)
        pygame.draw.rect(screen, SAPLING_TRUNK, trunk, border_radius=2)
        leaf_center = (rect.centerx, rect.y + 12)
        pygame.draw.circle(screen, SAPLING_LEAF_DARK, leaf_center, 10)
        pygame.draw.circle(screen, SAPLING_LEAF_LIGHT, (leaf_center[0] - 3, leaf_center[1] - 2), 6)

    def _draw_road_tree(self, screen, rect):
        trunk = pygame.Rect(rect.x, rect.y + 8, rect.w, rect.h - 12)
        pygame.draw.ellipse(screen, LOG_BARK, trunk)
        pygame.draw.ellipse(screen, LOG_RING, (trunk.x - 8, trunk.y + 2, 14, trunk.h - 4))
        pygame.draw.ellipse(screen, LOG_RING, (trunk.right - 6, trunk.y + 2, 14, trunk.h - 4))
        pygame.draw.ellipse(screen, LOG_MOSS, (trunk.x + 20, trunk.y + 3, max(20, trunk.w - 40), 6))

    def hit_test(self, car_x, distance, car_is_jumping, width, height):
        if car_is_jumping:
            return False
        return self.hit_test_entity(car_x, distance, width, height)

    def hit_test_entity(self, entity_x, entity_distance, width, height):
        entity_rect = pygame.Rect(0, 0, width, height)
        entity_rect.center = (int(entity_x), PLAYER_Y)
        for o in self.obstacles:
            sy = PLAYER_Y - (o["y"] - entity_distance)
            rect = pygame.Rect(0, 0, o["w"], o["h"])
            rect.center = (o["x"], int(sy))
            if rect.colliderect(entity_rect):
                return True
        return False


class Scenery:
    def __init__(self, map_key):
        self.map_key = map_key
        self.mode = MAP_PROFILES[map_key]["scenery"]
        self.bg_color = MAP_PROFILES[map_key]["bg"]
        self.items = []
        self.last_spawn_y = -120

    def reset(self):
        self.items = []
        self.last_spawn_y = -120

    def update(self, road, distance):
        spawn_until = distance + PLAYER_Y + 520
        while self.last_spawn_y < spawn_until:
            world_y = self.last_spawn_y + random.randint(24, 96)
            center = road.center_at(world_y)
            side = -1 if random.random() < 0.5 else 1
            offset = random.randint(ROAD_WIDTH // 2 + 65, ROAD_WIDTH // 2 + 280)
            x = int(center + side * offset)
            x = max(18, min(WIDTH - 18, x))
            item = {"x": x, "y": world_y}

            if self.mode == "forest":
                item["r"] = random.randint(12, 20)
                item["d"] = random.random() * math.pi * 2.0
            elif self.mode == "city":
                item["w"] = random.randint(26, 54)
                item["h"] = random.randint(42, 90)
            elif self.mode == "water":
                item["w"] = random.randint(26, 58)
                item["h"] = random.randint(14, 32)
            else:  # beach
                item["r"] = random.randint(10, 16)

            self.items.append(item)
            self.last_spawn_y = world_y + random.randint(40, 105)

        keep_from = distance - 220
        self.items = [t for t in self.items if t["y"] >= keep_from]

    def draw(self, screen, distance):
        visible = []
        for item in self.items:
            sy = PLAYER_Y - (item["y"] - distance)
            if -80 <= sy <= HEIGHT + 80:
                visible.append((sy, item))

        visible.sort(key=lambda entry: entry[0])
        for sy, item in visible:
            if self.mode == "forest":
                self._draw_forest_item(screen, item, sy, distance)
            elif self.mode == "city":
                self._draw_city_item(screen, item, sy)
            elif self.mode == "water":
                self._draw_water_item(screen, item, sy)
            else:
                self._draw_beach_item(screen, item, sy)

    def _draw_forest_item(self, screen, item, sy, distance):
        tx = item["x"]
        r = item["r"]
        pygame.draw.rect(screen, TREE_TRUNK, (tx - 4, int(sy) - 4, 8, r + 6), border_radius=2)
        pygame.draw.circle(screen, TREE_LEAF_DARK, (tx, int(sy) - r // 2), r)
        pygame.draw.circle(screen, TREE_LEAF_LIGHT, (tx - r // 3, int(sy) - r // 2 - 2), int(r * 0.55))
        disco_y = int(sy) - r - 6
        color_index = int((distance * 0.06 + item["d"] * 10.0)) % len(DISCO_COLORS)
        disco_color = DISCO_COLORS[color_index]
        pygame.draw.circle(screen, disco_color, (tx + r // 2, disco_y), 6)
        pygame.draw.circle(screen, (255, 255, 255), (tx + r // 2 - 2, disco_y - 2), 2)

    def _draw_city_item(self, screen, item, sy):
        w = item["w"]
        h = item["h"]
        rect = pygame.Rect(item["x"] - w // 2, int(sy) - h, w, h)
        pygame.draw.rect(screen, (70, 74, 92), rect, border_radius=4)
        for window_row in range(rect.y + 6, rect.bottom - 8, 12):
            for window_col in range(rect.x + 6, rect.right - 8, 10):
                pygame.draw.rect(screen, (222, 222, 160), (window_col, window_row, 5, 6), border_radius=1)

    def _draw_water_item(self, screen, item, sy):
        w = item["w"]
        h = item["h"]
        pond = pygame.Rect(item["x"] - w // 2, int(sy) - h // 2, w, h)
        pygame.draw.ellipse(screen, (66, 124, 198), pond)
        pygame.draw.ellipse(screen, (138, 205, 255), (pond.x + 3, pond.y + 2, pond.w - 6, max(4, pond.h // 2)))

    def _draw_beach_item(self, screen, item, sy):
        x = item["x"]
        r = item["r"]
        pygame.draw.circle(screen, (230, 208, 155), (x, int(sy)), r + 4)
        pygame.draw.rect(screen, (132, 97, 62), (x - 2, int(sy) - r - 8, 4, r + 10), border_radius=2)
        pygame.draw.circle(screen, (77, 152, 92), (x - 8, int(sy) - r - 10), 7)
        pygame.draw.circle(screen, (77, 152, 92), (x + 8, int(sy) - r - 10), 7)


def car_on_road(car_x, road, distance):
    center = road.center_at(distance)
    return abs(car_x - center) <= ROAD_WIDTH * 0.5 - 18


def road_side_limits(road, distance, car_x, half_width):
    centers = road.centers_at(distance)
    half_road = ROAD_WIDTH * 0.5
    if in_connector_zone(distance):
        left_road_center = min(centers)
        right_road_center = max(centers)
        left = left_road_center - half_road + half_width
        right = right_road_center + half_road - half_width
    else:
        center = min(centers, key=lambda c: abs(c - car_x))
        left = center - half_road + half_width
        right = center + half_road - half_width
    return left, right


def draw_bike(screen, x, y, bike_height, color):
    wheel_r = 7
    front = (x, y - bike_height // 2 + 14)
    rear = (x, y + bike_height // 2 - 14)
    pygame.draw.circle(screen, (30, 30, 35), front, wheel_r)
    pygame.draw.circle(screen, (30, 30, 35), rear, wheel_r)
    pygame.draw.line(screen, color, rear, (x + 8, y + 2), 4)
    pygame.draw.line(screen, color, (x + 8, y + 2), front, 4)
    pygame.draw.line(screen, color, (x + 8, y + 2), (x - 8, y - 8), 4)
    pygame.draw.circle(screen, (255, 230, 90), (x - 8, y - 8), 4)


def draw_rally_car(screen, x, y, width, height, color):
    rect = pygame.Rect(0, 0, width, height)
    rect.center = (x, y)
    pygame.draw.rect(screen, color, rect, border_radius=10)
    pygame.draw.rect(screen, (245, 235, 120), (rect.x + 8, rect.y + 8, rect.w - 16, 14), border_radius=3)
    pygame.draw.rect(screen, (40, 40, 40), (rect.x + 7, rect.bottom - 16, rect.w - 14, 10), border_radius=3)


def draw_bus(screen, x, y, width, height, color):
    rect = pygame.Rect(0, 0, width, height)
    rect.center = (x, y)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, (225, 225, 240), (rect.x + 6, rect.y + 8, rect.w - 12, 16), border_radius=3)
    pygame.draw.rect(screen, (225, 225, 240), (rect.x + 6, rect.y + 28, rect.w - 12, 14), border_radius=3)
    pygame.draw.rect(screen, (30, 30, 35), (rect.x + 4, rect.bottom - 18, rect.w - 8, 12), border_radius=3)


def load_highscores():
    if not HIGHSCORE_FILE.exists():
        return []
    try:
        data = json.loads(HIGHSCORE_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print("Enatystiedosto on virheellinen:", error)
        return []
    except OSError as error:
        print("Enatystiedoston lukeminen epaonnistui:", error)
        return []

    if not isinstance(data, list):
        print("Enatystiedoston muoto on virheellinen.")
        return []

    scores = []
    for item in data:
        if isinstance(item, int):
            scores.append(item)
    scores.sort(reverse=True)
    return scores[:5]


def save_highscores(scores):
    try:
        HIGHSCORE_FILE.write_text(
            json.dumps(scores[:5], ensure_ascii=True, indent=2),
            encoding="utf-8",
        )
    except OSError as error:
        print("Enatystiedoston tallennus epaonnistui:", error)


def main():
    pygame.display.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AI Game Jam - Jatkuva tie")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    small_font = pygame.font.Font(None, 24)

    selected_vehicle = 0
    selected_map = 0
    in_menu = True
    road = None
    car = None
    rival = None
    obstacles = None
    scenery = None
    distance = 0.0
    crashed = False
    score_recorded = False
    touching_rail = False
    highscores = load_highscores()
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif in_menu and (event.key == pygame.K_UP or event.key == pygame.K_w):
                    selected_vehicle = (selected_vehicle - 1) % len(VEHICLE_ORDER)
                elif in_menu and (event.key == pygame.K_DOWN or event.key == pygame.K_s):
                    selected_vehicle = (selected_vehicle + 1) % len(VEHICLE_ORDER)
                elif in_menu and (event.key == pygame.K_LEFT or event.key == pygame.K_a):
                    selected_map = (selected_map - 1) % len(MAP_ORDER)
                elif in_menu and (event.key == pygame.K_RIGHT or event.key == pygame.K_d):
                    selected_map = (selected_map + 1) % len(MAP_ORDER)
                elif in_menu and (event.key == pygame.K_RETURN or event.key == pygame.K_SPACE):
                    map_key = MAP_ORDER[selected_map]
                    road = Road()
                    car = Car(VEHICLE_ORDER[selected_vehicle])
                    rival = ComputerRider(road)
                    obstacles = ObstacleField()
                    scenery = Scenery(map_key)
                    distance = 0.0
                    crashed = False
                    score_recorded = False
                    touching_rail = False
                    in_menu = False
                elif event.key == pygame.K_SPACE and not crashed:
                    car.try_jump()
                elif event.key == pygame.K_r:
                    road = Road()
                    car.set_vehicle(VEHICLE_ORDER[selected_vehicle])
                    rival.reset(road)
                    obstacles.reset()
                    scenery.reset()
                    distance = 0.0
                    crashed = False
                    score_recorded = False
                    touching_rail = False

        if in_menu:
            screen.fill(MENU_BG)
            panel = pygame.Rect(WIDTH // 2 - 240, HEIGHT // 2 - 190, 480, 380)
            pygame.draw.rect(screen, MENU_PANEL, panel, border_radius=14)
            title = font.render("Valitse ajoneuvo", True, TEXT)
            screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 26))
            map_key = MAP_ORDER[selected_map]
            map_profile = MAP_PROFILES[map_key]
            map_line = small_font.render(
                "Maa: %s (%s)" % (map_profile["name"], map_profile["track"]),
                True,
                MAP_LABEL,
            )
            map_help = small_font.render("Vasen/Oikea: vaihda maa", True, MAP_LABEL)
            screen.blit(map_line, (panel.centerx - map_line.get_width() // 2, panel.y + 62))
            screen.blit(map_help, (panel.centerx - map_help.get_width() // 2, panel.y + 84))
            for idx, key in enumerate(VEHICLE_ORDER):
                row_y = panel.y + 126 + idx * 66
                row = pygame.Rect(panel.x + 40, row_y, panel.w - 80, 56)
                active = idx == selected_vehicle
                bg = MENU_HIGHLIGHT if active else (52, 52, 64)
                pygame.draw.rect(screen, bg, row, border_radius=10)
                name = small_font.render(VEHICLE_PROFILES[key]["name"], True, TEXT)
                screen.blit(name, (row.x + 16, row.y + 18))
            info = small_font.render("Ylos/Alas: ajoneuvo   Enter: aloita   ESC: lopeta", True, (220, 220, 220))
            screen.blit(info, (panel.centerx - info.get_width() // 2, panel.bottom - 32))
            pygame.display.flip()
            continue

        keys = pygame.key.get_pressed()
        if not crashed:
            car.update(keys)
            distance += car.speed
            scenery.update(road, distance)
            obstacles.update(road, distance)
            rival.update(road, obstacles, distance)
            touching_rail = False
            left_limit, right_limit = road_side_limits(road, distance, car.x, car.half_width)
            if car.x < left_limit:
                car.x = left_limit
                car.speed = max(1.4, car.speed * 0.92)
                touching_rail = True
            elif car.x > right_limit:
                car.x = right_limit
                car.speed = max(1.4, car.speed * 0.92)
                touching_rail = True
            if obstacles.hit_test(car.x, distance, car.is_jumping(), car.width, car.height):
                crashed = True
        elif not score_recorded:
            highscores.append(int(distance / 10))
            highscores.sort(reverse=True)
            del highscores[5:]
            save_highscores(highscores)
            score_recorded = True

        screen.fill(scenery.bg_color)
        scenery.draw(screen, distance)
        road.draw(screen, distance)
        obstacles.draw(screen, distance)
        rival.draw(screen, distance)
        car.draw(screen)

        hud = font.render("Nopeus: %d   Matka: %dm" % (int(car.speed * 10), int(distance / 10)), True, TEXT)
        controls = small_font.render("Nuolet/WASD: ohjaa   SPACE: hyppy   R: alusta   ESC: lopeta", True, TEXT)
        screen.blit(hud, (18, 16))
        screen.blit(controls, (18, 46))
        vehicle_text = small_font.render("Ajoneuvo: %s" % car.vehicle_name, True, (220, 220, 220))
        screen.blit(vehicle_text, (18, 100))
        map_profile = MAP_PROFILES[MAP_ORDER[selected_map]]
        map_text = small_font.render("Maa: %s (%s)" % (map_profile["name"], map_profile["track"]), True, (220, 220, 220))
        screen.blit(map_text, (18, 126))
        rival_gap = int((rival.distance - distance) / 10)
        if rival_gap >= 0:
            rival_text = small_font.render("Vastustaja: %dm edella" % rival_gap, True, (200, 220, 255))
        else:
            rival_text = small_font.render("Vastustaja: %dm jaljessa" % abs(rival_gap), True, (200, 220, 255))
        screen.blit(rival_text, (18, 74))
        if touching_rail and not crashed:
            warning = small_font.render("Kaide osuma: vauhti hidastuu", True, (255, 230, 120))
            screen.blit(warning, (18, 152))
        if crashed:
            msg = font.render("Törmäys! Paina R aloittaaksesi uudelleen.", True, (255, 230, 120))
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2))

        panel = pygame.Rect(WIDTH - 240, 16, 220, 180)
        pygame.draw.rect(screen, (30, 30, 35), panel, border_radius=8)
        title = small_font.render("Enatyslista", True, TEXT)
        screen.blit(title, (panel.x + 12, panel.y + 10))
        if highscores:
            for index, score in enumerate(highscores, start=1):
                row = small_font.render("%d. %dm" % (index, score), True, (230, 230, 230))
                screen.blit(row, (panel.x + 12, panel.y + 14 + index * 26))
        else:
            empty = small_font.render("Ei tuloksia viela", True, (200, 200, 200))
            screen.blit(empty, (panel.x + 12, panel.y + 44))

        pygame.display.flip()

    pygame.font.quit()
    pygame.display.quit()
    pygame.quit()


if __name__ == "__main__":
    main()
