import pygame
import asyncio

pygame.init()

screen = pygame.display.set_mode((800,600))

async def main():

    running = True

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

        screen.fill((0,180,255))

        pygame.display.flip()

        await asyncio.sleep(1/60)

asyncio.run(main())