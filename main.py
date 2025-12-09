from typing import Optional
import pygame
import random
import csv
import sys
import os.path
import matplotlib.pyplot as plt

N_TRIALS = 25

# there will be NUM_DELAYS different possible delay times, between 0 and MAX_WAIT_DELAY
MAX_WAIT_DELAY = 100
NUM_DELAYS = 5

# time to look at the grid before the change
VIEW_TIME = 2000

INSTRUCTIONS = [
    "Click on the character which changed as fast as possible.",
    "Press SPACE if you did not find it",
    "Press SPACE to start",
]

WIDTH = 1000
HEIGHT = 900

BG_COLOR = pygame.color.Color(0x28, 0x28, 0x28)

GRID_SIZE = 6
CASE_WIDTH = 60
CASE_HEIGHT = 70

GRID_START_X = WIDTH // 2 - GRID_SIZE * CASE_WIDTH // 2
GRID_START_Y = HEIGHT // 2 - GRID_SIZE * CASE_HEIGHT // 2


def create_window() -> pygame.Surface:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
    pygame.display.set_caption("Change Blindness Experiment")
    return screen


def clear_screen(screen: pygame.Surface, delay: Optional[int] = None) -> None:
    screen.fill(BG_COLOR)
    pygame.display.flip()
    if delay:
        pygame.time.delay(delay)


def load_images() -> list[pygame.Surface]:
    return [pygame.image.load(f"assets/image{i}.png").convert() for i in range(1, 5)]


def display_instruction(screen: pygame.Surface, texts: list[str]) -> None:
    myfont = pygame.font.SysFont("Times", 32)

    for i, text in enumerate(texts):
        line = myfont.render(
            text,
            0,
            pygame.Color("white"),
        )
        screen.blit(line, (100, HEIGHT // 2 + 60 * (-len(texts) // 2 + i)))

    pygame.display.flip()

    pygame.event.get()


def wait_for_keypress() -> None:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                return
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()


def wait_for_click() -> tuple[int, int, int]:
    "Waits for the user to click, and returns (x, y, delay)"
    start_time = pygame.time.get_ticks()
    pygame.event.get()
    max_delay = 5000

    while pygame.time.get_ticks() - start_time < max_delay:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                return (x, y, pygame.time.get_ticks() - start_time)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return (-1, -1, pygame.time.get_ticks() - start_time)
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

    return (-1, -1, max_delay)


def gen_grid() -> list[list[int]]:
    return [[random.randrange(4) for i in range(GRID_SIZE)] for j in range(GRID_SIZE)]


def display_grid(
    screen: pygame.Surface, images: list[pygame.Surface], grid: list[list[int]]
) -> None:
    clear_screen(screen)

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            image = images[grid[i][j]]
            screen.blit(
                image,
                (
                    GRID_START_X
                    + CASE_WIDTH * j
                    + (CASE_WIDTH - image.get_width()) // 2,
                    GRID_START_Y
                    + CASE_HEIGHT * i
                    + (CASE_HEIGHT - image.get_height()) // 2,
                ),
            )

    pygame.display.flip()


def run_test(
    screen: pygame.Surface,
    images: list[pygame.Surface],
    delay_hide: int,
) -> tuple[bool, int]:
    grid = gen_grid()

    display_grid(screen, images, grid)

    pygame.time.wait(VIEW_TIME)

    clear_screen(screen, delay_hide)

    change_i, change_j = random.randrange(GRID_SIZE), random.randrange(GRID_SIZE)

    # choose an image which is not the same as the original
    values = list(range(4))
    values.remove(grid[change_i][change_j])
    new_val = random.choice(values)

    grid[change_i][change_j] = new_val

    display_grid(screen, images, grid)

    x, y, delay = wait_for_click()
    click_i = (y - GRID_START_Y) // CASE_HEIGHT
    click_j = (x - GRID_START_X) // CASE_WIDTH

    if click_i != change_i or click_j != change_j:
        display_grid(screen, images, grid)
        pygame.draw.circle(
            screen,
            (255, 0, 0),
            (
                GRID_START_X + (change_j + 0.5) * CASE_WIDTH,
                GRID_START_Y + (change_i + 0.5) * CASE_HEIGHT,
            ),
            max(CASE_WIDTH, CASE_HEIGHT) * 0.6,
            width=5,
        )
        pygame.display.flip()
        pygame.time.wait(1000)

    return (click_i == change_i and click_j == change_j, delay)


def display_results(filename: str) -> None:
    results = []

    with open(filename) as f:
        reader = csv.reader(f, delimiter=" ")
        for line in reader:
            results.append(list(map(int, line)))

    # success_rates[success] = (n_success, n_experiments)
    success_rates: dict[int, list[int]] = {}

    for time, success, _ in results:
        if time not in success_rates:
            success_rates[time] = [0, 0]

        success_rates[time][0] += success
        success_rates[time][1] += 1

    xs: list[int] = []
    ys: list[float] = []

    for key, (success, tot) in sorted(success_rates.items()):
        xs.append(key)
        ys.append(success / tot)

    plt.plot(xs, ys, "ro")
    plt.xticks(xs)
    plt.xlabel("Blank screen delay (ms)")
    plt.ylabel("Success rate")

    plt.show()


def main() -> None:
    screen = create_window()
    images = load_images()

    clear_screen(screen)
    display_instruction(screen, INSTRUCTIONS)
    wait_for_keypress()

    clear_screen(screen, 500)

    wait_times = [i * MAX_WAIT_DELAY // (NUM_DELAYS - 1) for i in range(NUM_DELAYS)] * (
        N_TRIALS // NUM_DELAYS
    )
    random.shuffle(wait_times)

    # list of (wait_time, ok, click_delay)
    results: list[tuple[int, int, int]] = []

    for wait_time in wait_times:
        clear_screen(screen)
        display_instruction(screen, ["Ready..."])
        pygame.time.wait(1000)

        ok, click_delay = run_test(screen, images, wait_time)
        print(wait_time, ok)
        results.append((wait_time, int(ok), click_delay))

    # sort by wait time
    results.sort()

    i_file = 0
    while os.path.isfile(f"data/result{i_file}.csv"):
        i_file += 1

    with open(f"data/result{i_file}.csv", "w", newline="") as f:
        writer = csv.writer(f, delimiter=" ")
        writer.writerows(results)

    print(f"\nWrote results in data/result{i_file}.csv")

    pygame.quit()

    display_results(f"data/result{i_file}.csv")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        display_results(sys.argv[1])
    else:
        main()
