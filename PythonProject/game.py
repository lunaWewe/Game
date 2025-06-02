import pygame
import random

# 初始化 Pygame
pygame.init()

# 設定視窗
width, height = 800, 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("2D 動作遊戲")

# 顏色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# 主角類
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (width // 2, height // 2)
        self.attack_speed = 500  # 攻擊間隔（毫秒）
        self.attack_type = 1  # 攻擊類型（1=普通，2=快速，3=強力）
        self.gems = 0  # 收集的寶石數
        self.last_attack = pygame.time.get_ticks()

    def update(self):
        self.rect.center = pygame.mouse.get_pos()

    def attack(self, enemies):
        now = pygame.time.get_ticks()
        if now - self.last_attack >= self.attack_speed:
            self.last_attack = now
            mouse_pos = pygame.mouse.get_pos()
            for enemy in enemies:
                if enemy.alive and enemy.rect.collidepoint(mouse_pos):
                    enemy.die()
                    return True
        return False

# 敵人類
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.alive = True

    def die(self):
        self.alive = False
        self.image = pygame.Surface((15, 15))
        self.image.fill(GREEN)  # 變成寶石

# 門類
class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 100))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.closed = True

# 初始化遊戲物件
player = Player()
player_group = pygame.sprite.Group(player)
enemies = pygame.sprite.Group()
doors = pygame.sprite.Group()

# 生成初始關卡
def setup_level(level):
    enemies.empty()
    for _ in range(5 + level * 2):  # 每關增加敵人數量
        x = random.randint(100, width - 100)
        y = random.randint(100, height - 100)
        enemies.add(Enemy(x, y))
    doors.empty()
    doors.add(Door(50, height // 2 - 50))  # 左門
    doors.add(Door(width - 60, height // 2 - 50))  # 右門

# 初始關卡
level = 1
setup_level(level)
in_level = False

# 遊戲主迴圈
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not in_level:
                in_level = True  # 點擊進入關卡
            else:
                # 攻擊並檢查寶石
                if player.attack(enemies):
                    player.gems += 1
                    # 升級邏輯
                    if player.gems >= 5:
                        if player.attack_type == 1:
                            player.attack_speed = 300  # 提升攻擊速度
                            player.attack_type = 2
                        elif player.attack_type == 2:
                            player.attack_speed = 200  # 強力攻擊
                            player.attack_type = 3
                        player.gems = 0  # 重置寶石

    # 更新
    if in_level:
        player.update()
        # 檢查是否所有敵人死亡
        all_dead = all(not enemy.alive for enemy in enemies)
        if all_dead:
            for door in doors:
                door.closed = False
                door.image = pygame.Surface((0, 0))  # 門打開
            in_level = False
            level += 1  # 進入下一關
            setup_level(level)

    # 繪製
    window.fill(BLACK)
    doors.draw(window)
    enemies.draw(window)
    player_group.draw(window)
    # 顯示關卡和寶石數
    font = pygame.font.Font(None, 36)
    text = font.render(f"Level: {level} Gems: {player.gems}", True, WHITE)
    window.blit(text, (10, 10))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()