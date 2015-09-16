from pygame.locals import *
import pygame, pygame.font, pygame.event, pygame.draw, string
import os

srcdir = os.path.dirname(os.path.realpath(__file__))

start_event = pygame.USEREVENT + 1
pause1_event = pygame.USEREVENT + 2
out_event = pygame.USEREVENT + 3
pause2_event = pygame.USEREVENT + 4

tick = pygame.USEREVENT + 5
short_delay_event = pygame.USEREVENT + 6
delay_event = pygame.USEREVENT + 7

short_pause = 1000  # ms
long_pause = 1000  # ms

stages = [start_event, pause1_event, out_event, pause2_event]

sounds = {start_event: 'inhale.wav',
          pause1_event: 'break.wav',
          out_event: 'exhale.wav',
          pause2_event: 'break.wav'}

colors = {start_event: (124, 124, 124),
          pause1_event: (144, 124, 124),
          out_event: (184, 124, 124),
          pause2_event: (144, 124, 124)}

size = width, height = (500, 400)
bar = bw, bh = (400, 50)


def get_key():
    while 1:
        event = pygame.event.poll()
        if event.type == KEYDOWN:
            return event.key
        else:
            pass


def display_box(screen, message):
    fontobject = pygame.font.Font(None, 18)
    pygame.draw.rect(screen, (0, 0, 0),
                     ((screen.get_width() / 2) - 100,
                      screen.get_height() - 70,
                      200, 20), 0)
    pygame.draw.rect(screen, (255, 255, 255),
                     ((screen.get_width() / 2) - 102,
                      screen.get_height() - 72,
                      204, 24), 1)
    if len(message) != 0:
        screen.blit(fontobject.render(message, 1, (255, 255, 255)),
                    ((screen.get_width() / 2) - 100, screen.get_height() - 70))
    pygame.display.flip()


def ask(screen, question):
    pygame.font.init()
    current_string = []
    display_box(screen, question + ': ' + string.join(current_string, ''))
    while 1:
        inkey = get_key()
        if inkey == K_BACKSPACE:
            current_string = current_string[0:-1]
        elif inkey == K_RETURN:
            break
        elif inkey == K_MINUS:
            current_string.append('_')
        elif inkey <= 127:
            current_string.append(chr(inkey))
        display_box(screen, question + ': ' + string.join(current_string, ''))
    return string.join(current_string, '')


def delay(short=True):
    pygame.time.set_timer(tick, 0)
    if not short:
        pygame.mixer.music.stop()
        pygame.time.set_timer(delay_event, short_pause)
        pygame.time.set_timer(short_delay_event, 0)
    else:
        pygame.time.set_timer(short_delay_event, short_pause)


def update_stage(stage):
    pygame.mixer.music.load(os.path.join(srcdir, sounds[stage]))
    pygame.mixer.music.play(-1)
    pygame.time.set_timer(delay_event, 0)
    pygame.time.set_timer(tick, 1000)


def end():
    pygame.mixer.music.stop()
    pygame.time.set_timer(tick, 0)


if __name__ == '__main__':
    window = pygame.display.set_mode(size)
    pygame.display.set_caption('Pranayama')
    rawicon=pygame.image.load(os.path.join(srcdir, 'meditation_sun_yCo_icon.ico'))
    pygame.display.set_icon(rawicon)
    background = pygame.image.load(os.path.join(srcdir, 'meditation_sun.jpg'))
    background.convert_alpha()
    window.blit(background, (0, 0))
    pygame.mixer.init()
    pygame.mixer.music.load(os.path.join(srcdir, 'shaolin.mp3'))
    pygame.mixer.music.play(-1)

    # Ask about stages in seconds
    breath = int(ask(window, 'Inhale'))
    pause1 = int(ask(window, 'Pause #1'))
    outward = int(ask(window, 'Exhale'))
    pause2 = int(ask(window, 'Pause #2'))
    iters = int(ask(window, 'Iterations'))

    full_time = breath + pause1 + outward + pause2
    bw = int(bw - bw % full_time)
    bar = (bw, bh)
    px_per_sec = int(bw / full_time)
    xoffset = window.get_rect().centerx - (bw + 1) / 2

    def draw_rect():
        s1 = pygame.Surface((px_per_sec * breath, bh))
        s1.fill(colors[stages[0]])
        s2 = pygame.Surface((px_per_sec * pause1, bh))
        s2.fill(colors[stages[1]])
        s3 = pygame.Surface((px_per_sec * outward, bh))
        s3.fill(colors[stages[2]])
        s4 = pygame.Surface((px_per_sec * pause2, bh))
        s4.fill(colors[stages[3]])
        window.blit(s1, (xoffset, 300))
        window.blit(s2, (xoffset + s1.get_width(), 300))
        window.blit(s3, (xoffset + s1.get_width() + s2.get_width(), 300))
        window.blit(s4, (xoffset + s1.get_width() + s2.get_width() + s3.get_width(), 300))

    def progress(t):
        bar = pygame.Surface((px_per_sec, bh))
        bar.set_alpha(60)
        bar.fill((255, 0, 0))
        window.blit(bar, (xoffset + px_per_sec * t, 300))

    event_time = {0: start_event,
                  breath: pause1_event,
                  breath + pause1: out_event,
                  breath + pause1 + outward: pause2_event}

    time = 0
    loop = 1

    window.blit(background, (0, 0))
    font = pygame.font.Font(None, 36)
    looptext = 'Loop:%s' + ('/%s' % iters)
    text = font.render(looptext % loop, 1, (10, 10, 10))
    textpos = text.get_rect()
    textpos.centerx = window.get_rect().centerx
    r = text.get_rect()
    text_layout = window.subsurface(r.x, r.y, width, r.height).copy()
    window.blit(text, textpos)

    draw_rect()
    delay(short=False)

    running = True
    while running:
        pygame.display.update()
        for e in pygame.event.get():
            if e.type == tick:
                progress(time)
                time += 1
                if time in event_time.keys():
                    delay()
            elif e.type == pygame.QUIT:
                running = False
            elif e.type == short_delay_event:
                delay(short=False)
            elif e.type == delay_event:
                update_stage(event_time[time])
                if time == 0:
                    draw_rect()
            if time == full_time:
                if loop < iters:
                    loop += 1
                    time = 0
                    text = font.render(looptext % loop, 1, (10, 10, 10))
                    window.blit(text_layout, text_layout.get_rect())
                    window.blit(text, textpos)
                    delay()
                else:
                    end()

    pygame.quit()