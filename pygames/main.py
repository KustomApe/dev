import pygame

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Super Python Mario')

clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((32, 32))
        self.image.fill((255, 0, 0))  # 赤い四角形でプレイヤーを表現
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = WINDOW_HEIGHT - 64
        self.velocity_y = 0
        self.jumping = False

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT]:
            self.rect.x += 5
        if keys[pygame.K_SPACE] and not self.jumping:
            self.velocity_y = -15
            self.jumping = True

        # 重力の適用
        self.velocity_y += 0.8
        self.rect.y += self.velocity_y

        # 地面との衝突判定
        if self.rect.bottom > WINDOW_HEIGHT - 32:
            self.rect.bottom = WINDOW_HEIGHT - 32
            self.jumping = False
            self.velocity_y = 0

player = Player()
all_sprites = pygame.sprite.Group(player)

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 255, 0))  # 緑色のプラットフォーム
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

platforms = pygame.sprite.Group()
platforms.add(Platform(0, WINDOW_HEIGHT - 32, WINDOW_WIDTH, 32))  # 地面
platforms.add(Platform(300, 400, 100, 20))  # プラットフォーム

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()

    # プラットフォームとの衝突判定
    hits = pygame.sprite.spritecollide(player, platforms, False)
    if hits:
        player.rect.bottom = hits[0].rect.top
        player.jumping = False
        player.velocity_y = 0

    screen.fill((135, 206, 235))  # 空色の背景
    all_sprites.draw(screen)
    platforms.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
