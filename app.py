import pygame as pg
from test_c import *

pg.init()

FPS = 40
X, Y = 800, 600
TEXT_FONT = pg.font.SysFont('Arial', 28)


BUTTON_CLICK = pg.mixer.Sound('button_click.mp3')


class Button(pg.sprite.Sprite):
    def __init__(self, group, pos, text, func):
        super().__init__(group)
        self.func = func
        text_sur = TEXT_FONT.render(text, 1, 'white')
        self.image = pg.surface.Surface((text_sur.get_width() + 20, text_sur.get_height() + 20))
        self.image.fill('orange')
        self.image.blit(text_sur, (10, 10))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.mouse_on = self.rect.x + 5, self.rect.y + 5
        self.mouse_not_on = self.rect.x, self.rect.y

    def event(self, e):
        if e.type == pg.MOUSEMOTION and self.rect.collidepoint(e.pos):
            self.rect.x, self.rect.y = self.mouse_on
        else:
            self.rect.x, self.rect.y = self.mouse_not_on
        if e.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(e.pos):
            self.func()
            BUTTON_CLICK.play(loops=0)


class Table(pg.sprite.Sprite):
    def __init__(self, pos, size):
        super().__init__()
        self.filenames = []
        self.rect = pg.rect.Rect(*pos, *size)
        self.value = 0
        self.filename_font = pg.font.SysFont('Arial', 14)
        self.number_font = pg.font.SysFont('Arial', 12)

    def update_list(self, updated_filenames):
        self.filenames = updated_filenames

    def draw(self, screen):
        rect = pg.rect.Rect(self.rect.x + 1, self.rect.y + 1, 320, 40)
        pg.draw.rect(screen, 'black', self.rect, width=1)
        for i, file in enumerate(self.filenames):
            if i * 40 >= self.rect.h:
                break
            filename_t, size = file
            surface = pg.surface.Surface((rect.w, rect.h))
            count = self.number_font.render('№' + str(i + 1), 1, 'red')
            filename = self.filename_font.render(filename_t + '  |  ' + str(size) + 'Б', 1, 'orange')
            surface.fill('white')
            surface.blit(count, (5, 7))
            surface.blit(filename, (30, 5))
            screen.blit(surface, (rect.x, rect.y))
            rect.y += 40

    def event(self, e):
        mouse_pos = pg.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            if e.type == pg.MOUSEWHEEL:
                if self.value > 3:
                    self.value = 0
                    file = self.filenames.pop(0)
                    self.filenames.append(file)
                self.value += 1

    def get_current(self):
        if not self.filenames:
            return None
        else:
            return self.filenames[0]


def main():
    global FPS, X, Y

    screen = pg.display.set_mode((X, Y))
    clock = pg.time.Clock()

    page1 = pg.sprite.Group()

    def send_solution_func(file):
        if file:
            send_solution(file)

    table = Table((X * 0.1, Y * 0.15), (X * 0.5, Y * 0.7))
    but_upload = Button(page1, (X * 0.65, Y * 0.3), 'Upload some file', lambda: send_solution_func(current_file))
    but_list = Button(page1, (X * 0.65, Y * 0.42), 'Get list of files', lambda: table.update_list(get_filenames()))
    but_download = Button(page1, (X * 0.65, Y * 0.54), 'Download first file',
                          lambda: get_solution(table.get_current()[0]))

    current_file = None

    is_running = True
    while is_running:
        screen.fill('white')
        for e in pg.event.get():
            if e.type == pg.QUIT:
                is_running = False
            elif e.type == pg.DROPFILE:
                current_file = e.file
            try:
                but_upload.event(e)
                but_list.event(e)
                but_download.event(e)
                table.event(e)
            except Exception as error:
                print(error)
        table.draw(screen)
        clock.tick(FPS)
        page1.draw(screen)
        screen.blit(TEXT_FONT.render(f'Выбранный файл: {current_file or "НИЧЕГО"}', 1, 'black'), (20, 10))
        screen.blit(TEXT_FONT.render(f'Всего: {len(table.filenames)}', 1, 'black'), (X * 0.11, Y * 0.86))
        pg.display.flip()
        pass


if __name__ == '__main__':
    main()
