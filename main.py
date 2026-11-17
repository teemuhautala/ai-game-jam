"""AI Game Jam: a tiny, offline, beginner-friendly pygame-ce starter."""

import pygame

WIDTH, HEIGHT = 960, 640
FPS = 60
GRASS = (69, 135, 82)


def draw_track(screen):
    screen.fill(GRASS)


def main():
    # Initialize only the modules this starter game uses.
    pygame.display.init()
    pygame.font.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AI Game Jam - Ajopeli")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 27)
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        draw_track(screen)
        info = font.render("ESC: lopeta", True, (255, 255, 255))
        screen.blit(info, (22, 18))
        pygame.display.flip()

    pygame.font.quit()
    pygame.display.quit()
    pygame.quit()


if __name__ == "__main__":
    main()
