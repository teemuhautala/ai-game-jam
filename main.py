"""AI Game Jam: a tiny, offline, beginner-friendly pygame-ce starter."""

import math

import pygame

WIDTH, HEIGHT = 960, 640
FPS = 60

GRASS = (69, 135, 82)
MOWED_GRASS = (92, 155, 100)
ROAD = (65, 65, 72)
LANE = (250, 250, 250)
CAR_COLOR = (220, 70, 70)
TEXT = (255, 255, 255)

OUTER_TRACK = pygame.Rect(80, 60, 800, 520)
INNER_TRACK = pygame.Rect(260, 180, 440, 280)
START_LINE = pygame.Rect(
    OUTER_TRACK.centerx - 7, OUTER_TRACK.top + 8, 14, INNER_TRACK.top - OUTER_TRACK.top - 16
)

CHECKPOINTS = [
    pygame.Rect(OUTER_TRACK.right - 120, OUTER_TRACK.top + 8, 100, 40),
    pygame.Rect(OUTER_TRACK.right - 80, OUTER_TRACK.centery - 20, 40, 80),
    pygame.Rect(OUTER_TRACK.centerx - 50, OUTER_TRACK.bottom - 48, 100, 40),
    pygame.Rect(OUTER_TRACK.left + 40, OUTER_TRACK.centery - 20, 40, 80),
]


def is_on_road(position):
    point = (int(position.x), int(position.y))
    return OUTER_TRACK.collidepoint(point) and not INNER_TRACK.collidepoint(point)


def crossed_rect(start_pos, end_pos, rect):
    return rect.clipline(
        (int(start_pos.x), int(start_pos.y)),
        (int(end_pos.x), int(end_pos.y)),
    )


def draw_track(screen, mowed_marks):
    screen.fill(GRASS)
    for point in mowed_marks:
        pygame.draw.circle(screen, MOWED_GRASS, point, 12)
    pygame.draw.rect(screen, ROAD, OUTER_TRACK, border_radius=48)
    pygame.draw.rect(screen, GRASS, INNER_TRACK, border_radius=38)
    pygame.draw.rect(screen, LANE, START_LINE)

    lane_width = (OUTER_TRACK.width - INNER_TRACK.width) // 2
    lane_height = (OUTER_TRACK.height - INNER_TRACK.height) // 2
    dashes = 20
    for i in range(dashes):
        t = i / dashes
        x_top = OUTER_TRACK.left + lane_width + t * INNER_TRACK.width
        y_left = OUTER_TRACK.top + lane_height + t * INNER_TRACK.height
        pygame.draw.circle(screen, LANE, (int(x_top), OUTER_TRACK.top + lane_height // 2), 3)
        pygame.draw.circle(screen, LANE, (OUTER_TRACK.right - lane_width // 2, int(y_left)), 3)
        pygame.draw.circle(screen, LANE, (int(x_top), OUTER_TRACK.bottom - lane_height // 2), 3)
        pygame.draw.circle(screen, LANE, (OUTER_TRACK.left + lane_width // 2, int(y_left)), 3)


class Car:
    def __init__(self):
        self.start_pos = pygame.Vector2(START_LINE.centerx, START_LINE.centery + 20)
        self.start_angle = -90
        self.max_speed = 6.3
        self.max_reverse = -2.8
        self.acceleration = 0.2
        self.brake = 0.3
        self.friction = 0.94
        self.turn_speed = 2.8
        self.offroad_drag = 0.84
        self.reset()

    def reset(self):
        self.pos = self.start_pos.copy()
        self.prev_pos = self.pos.copy()
        self.angle = self.start_angle
        self.speed = 0.0
        self.offroad = False

    def update(self, keys):
        self.prev_pos = self.pos.copy()
        forward = keys[pygame.K_UP] or keys[pygame.K_w]
        backward = keys[pygame.K_DOWN] or keys[pygame.K_s]
        turn_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        turn_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

        if forward and not backward:
            self.speed += self.acceleration
        if backward and not forward:
            if self.speed > 0:
                self.speed -= self.brake
            else:
                self.speed -= self.acceleration

        self.speed *= self.friction
        self.speed = max(self.max_reverse, min(self.max_speed, self.speed))
        if abs(self.speed) < 0.03:
            self.speed = 0.0

        steer = 0.0
        if turn_left:
            steer -= 1.0
        if turn_right:
            steer += 1.0

        next_angle = self.angle
        if steer != 0:
            if self.speed == 0:
                next_angle += steer * (self.turn_speed * 0.55)
            else:
                speed_factor = max(0.35, abs(self.speed) / self.max_speed)
                steering_direction = 1.0 if self.speed > 0 else -1.0
                next_angle += steer * self.turn_speed * speed_factor * steering_direction

        self.angle = next_angle

        rad = math.radians(self.angle)
        direction = pygame.Vector2(math.cos(rad), math.sin(rad))
        next_pos = self.pos + direction * self.speed
        self.pos = next_pos
        self.pos.x = max(16, min(WIDTH - 16, self.pos.x))
        self.pos.y = max(16, min(HEIGHT - 16, self.pos.y))

        self.offroad = not is_on_road(self.pos)
        if self.offroad:
            self.speed *= self.offroad_drag

    def draw(self, screen):
        car_surface = pygame.Surface((52, 28), pygame.SRCALPHA)
        pygame.draw.rect(car_surface, CAR_COLOR, (0, 0, 52, 28), border_radius=7)

        # Rear marker
        pygame.draw.rect(car_surface, (70, 30, 30), (0, 2, 9, 24), border_radius=4)
        # Front marker + arrow so heading is obvious even when standing still.
        pygame.draw.rect(car_surface, (245, 230, 90), (41, 4, 11, 20), border_radius=3)
        pygame.draw.polygon(car_surface, (255, 255, 255), [(38, 14), (26, 8), (26, 20)])

        rotated = pygame.transform.rotate(car_surface, -self.angle)
        rect = rotated.get_rect(center=(self.pos.x, self.pos.y))
        screen.blit(rotated, rect)


def main():
    pygame.display.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AI Game Jam - Ajopeli")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 30)
    small_font = pygame.font.Font(None, 24)

    car = Car()
    lap = 0
    checkpoint_index = 0
    race_started = False
    mowed_marks = []
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    car.reset()
                    lap = 0
                    checkpoint_index = 0
                    race_started = False
                    mowed_marks = []

        keys = pygame.key.get_pressed()
        car.update(keys)

        if checkpoint_index < len(CHECKPOINTS):
            checkpoint = CHECKPOINTS[checkpoint_index]
            if crossed_rect(car.prev_pos, car.pos, checkpoint):
                checkpoint_index += 1

        prev_on_start_line = START_LINE.collidepoint(int(car.prev_pos.x), int(car.prev_pos.y))
        on_start_line = START_LINE.collidepoint(int(car.pos.x), int(car.pos.y))
        if not race_started and not on_start_line:
            race_started = True

        entered_start_line = on_start_line and not prev_on_start_line
        moving_right = car.pos.x > car.prev_pos.x
        if entered_start_line and race_started and moving_right and checkpoint_index == len(CHECKPOINTS):
            lap += 1
            checkpoint_index = 0

        if car.offroad:
            mowed_marks.append((int(car.pos.x), int(car.pos.y)))
            if len(mowed_marks) > 4000:
                mowed_marks = mowed_marks[-4000:]

        draw_track(screen, mowed_marks)
        car.draw(screen)

        speed_kmh = abs(car.speed) * 42
        hud = font.render("Nopeus: %3d km/h   Kierrokset: %d" % (speed_kmh, lap), True, TEXT)
        controls = small_font.render(
            "Nuolet/WASD: aja   R: alusta   ESC: lopeta", True, TEXT
        )
        screen.blit(hud, (20, 18))
        screen.blit(controls, (20, 50))
        if car.offroad:
            warning = small_font.render("Nurmikko hidastaa ja leikkaantyy!", True, (255, 240, 120))
            screen.blit(warning, (20, 78))

        pygame.display.flip()

    pygame.font.quit()
    pygame.display.quit()
    pygame.quit()


if __name__ == "__main__":
    main()
