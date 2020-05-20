import pygame
import numpy as np

DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 600
MILLIS_IN_SECONDS = 1000
PIXELS_IN_METER = 50
G = 9.89


class Particle(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, rect: pygame.Rect):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = rect

    @classmethod
    def from_manager(cls, manager: "ParticleManager", idx: int):
        return cls(manager.surfaces[idx], manager.rects[idx])


class ParticleManager:
    PARTICLE_COLOR = (0, 0, 0)
    def __init__(self, x, y, surf_x, surf_y, dx, dy, radius):
        self.x = x
        self.y = y
        self.surf_x = surf_x
        self.surf_y = surf_y
        self.dx = dx
        self.dy = dy
        self.radius = radius

        self.surfaces = [
            pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA, 32)
            for _ in range(self.x.size)
        ]
        self.rects = [surf.get_rect() for surf in self.surfaces]
        for surface in self.surfaces:
            pygame.draw.circle(surface,
                               self.PARTICLE_COLOR,
                               (radius, radius),
                               radius)
        self.particles = [Particle.from_manager(self, idx) for idx, _ in enumerate(self.surfaces)]
        self.sprite_group = pygame.sprite.Group(*self.particles)


    @classmethod
    def create_at_random_points(cls, quantity: int, radius: int):
        x = np.random.randint(radius, DISPLAY_WIDTH - radius, quantity).astype(np.float64)
        y = np.random.randint(radius, DISPLAY_HEIGHT - radius, quantity).astype(np.float64)
        surf_x = x - radius
        surf_y = y - radius
        dx = np.random.uniform(-2, 2, x.shape).astype(np.float64) * 3
        dy = np.random.uniform(-2, 2, x.shape).astype(np.float64) * 3
        return cls(x, y, surf_x, surf_y, dx, dy, radius)

    def draw(self, display):
        self.sprite_group.draw(display)


    def tick(self, time_delta_millis):
        time_delta_sec = (time_delta_millis / MILLIS_IN_SECONDS)

        delta_x = time_delta_sec * PIXELS_IN_METER * self.dx
        delta_y = time_delta_sec * PIXELS_IN_METER * self.dy
        self.x += delta_x
        self.y += delta_y
        self.surf_x += delta_x
        self.surf_y += delta_y
        self.dy += time_delta_sec * G

        # Not physically accurate.
        self.dy *= 0.995
        self.dx *= 0.995

        self.dx[self.x < 0] *= np.sign(self.dx[self.x < 0])  # Ensure positive.
        self.dy[self.y < 0] *= np.sign(self.dx[self.y < 0])  # Ensure positive.
        self.dx[self.x > DISPLAY_WIDTH] *= -np.sign(self.dx[self.x > DISPLAY_WIDTH])  # Ensure negative.
        self.dy[self.y > DISPLAY_HEIGHT] *= -np.sign(self.dy[self.y > DISPLAY_HEIGHT])  # Ensure negative.

        # Update particles.
        for x, y, rect in zip(self.x, self.y, self.rects):
            rect.x = x
            rect.y = y

def init():
    pygame.init()
    display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    pygame.display.set_caption("Particles")
    clock = pygame.time.Clock()
    return display, clock


def main_loop(display, clock):
    exit = False
    particles = ParticleManager.create_at_random_points(1000, 5)

    current_time_millis = 0
    while not exit:
        time_delta_millis = clock.get_time()
        current_time_millis += time_delta_millis

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit = True
        display.fill((255, 255, 255))

        particles.tick(time_delta_millis)
        particles.draw(display)

        pygame.display.update()
        clock.tick(60)


def main():
    display, clock = init()
    main_loop(display, clock)
    pygame.quit()
    quit()

if __name__ == "__main__":
    main()