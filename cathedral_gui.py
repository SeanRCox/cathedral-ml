import pygame as pg
#import Board from board

SCREEN_SIZE = 1400
GRID_SIZE = 10
CELL_SIZE = 600 // GRID_SIZE
LINE_COLOR = (0,0,0)

class Cathedral_GUI:
    def __init__(self):
        
        pg.init()
        self._screen = pg.display.set_mode((SCREEN_SIZE, SCREEN_SIZE-800))
        pg.display.set_caption("Cathedral")
        game_running = True
        while game_running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    game_running = False
                #include other conditionals here later

            self._screen.fill((255, 255, 255))
            for x in range(GRID_SIZE + 1):
                pg.draw.line(self._screen, LINE_COLOR, ((x * CELL_SIZE), 0), (x * CELL_SIZE, SCREEN_SIZE-800))
            for y in range(GRID_SIZE + 1):
                pg.draw.line(self._screen, LINE_COLOR, (0, (y * CELL_SIZE)), (SCREEN_SIZE-800, y * CELL_SIZE))

            sprite_image = pg.image.load('piece_images/r_inn.png')
            self._screen.blit(sprite_image, (0, 0))


            pg.display.update()

        pg.quit()

Cathedral_GUI()