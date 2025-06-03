import pygame
import random
import os
import math
import time

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
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# 檢查資源檔案是否存在
def load_resource(filename, default_surface):
    if os.path.exists(filename):
        return pygame.image.load(filename).convert_alpha()
    return default_surface

# 子彈類
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        default_surface = pygame.Surface((5, 5))
        default_surface.fill(YELLOW)
        self.image = load_resource("bullet.png", default_surface)
        self.image = pygame.transform.scale(self.image, (5, 5))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.right < 0 or self.rect.left > width or self.rect.bottom < 0 or self.rect.top > height:
            self.kill()

# 道具類
class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, item_type):
        super().__init__()
        default_surface = pygame.Surface((15, 15))
        default_surface.fill(PURPLE)
        self.image = load_resource("item.png", default_surface)
        self.image = pygame.transform.scale(self.image, (15, 15))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.type = item_type  # "speed" 或 "multi"

# 主角類
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        default_surface = pygame.Surface((30, 30))
        default_surface.fill(BLUE)
        self.image = load_resource("player.png", default_surface)  # 載入主角圖片
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        self.rect.center = (width // 2, height // 2)
        self.base_attack_speed = 500
        self.attack_speed = self.base_attack_speed
        self.attack_type = 1
        self.gems = 0
        self.last_attack = pygame.time.get_ticks()
        self.item_effect = None
        self.item_duration = 0
        self.item_start_time = 0

    def update(self):
        self.rect.center = pygame.mouse.get_pos()
        if self.item_effect:
            elapsed = time.time() - self.item_start_time
            self.item_duration = 5 - elapsed
            if elapsed >= 5:
                self.item_effect = None
                self.attack_speed = self.base_attack_speed
        self.shoot_angles = [0, -math.pi / 6, math.pi / 6]
        if self.item_effect == "multi":
            self.shoot_angles = [-math.pi / 4, -math.pi / 8, 0, math.pi / 8, math.pi / 4]

    def shoot(self, bullets):
        now = pygame.time.get_ticks()
        if now - self.last_attack >= self.attack_speed:
            self.last_attack = now
            for angle in self.shoot_angles:
                bullet = Bullet(self.rect.centerx, self.rect.centery, angle)
                bullets.add(bullet)
            return True
        return False

    def apply_item(self, item_type):
        self.item_effect = item_type
        self.item_start_time = time.time()
        self.item_duration = 5
        if item_type == "speed":
            self.attack_speed = self.base_attack_speed // 2
        elif item_type == "multi":
            self.attack_speed = self.base_attack_speed

    def collect_gem(self, enemy):
        self.gems += 1
        if os.path.exists("gem.wav"):
            sound = pygame.mixer.Sound("gem.wav")
            sound.play()
        enemy.kill()  # 移除寶石（敵人）
        if self.gems >= 5:
            if self.attack_type == 1:
                self.base_attack_speed = 300
                self.attack_speed = 300
                self.attack_type = 2
            elif self.attack_type == 2:
                self.base_attack_speed = 200
                self.attack_speed = 200
                self.attack_type = 3
            self.gems = 0

# 敵人類
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, level):
        super().__init__()
        default_surface = pygame.Surface((20, 20))
        default_surface.fill(RED)
        self.image = load_resource("enemy.png", default_surface)
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.alive = True
        self.hp = 3 + level // 2
        self.max_hp = self.hp
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = 2
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed
        self.font = pygame.font.Font(None, 24)

    def update(self):
        if self.alive:
            self.rect.x += self.dx
            self.rect.y += self.dy
            if self.rect.left < 100 or self.rect.right > width - 100:
                self.dx = -self.dx
                self.angle = math.atan2(self.dy, self.dx)
            if self.rect.top < 100 or self.rect.bottom > height - 100:
                self.dy = -self.dy
                self.angle = math.atan2(self.dy, self.dx)

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.die()

    def die(self):
        self.alive = False
        default_surface = pygame.Surface((15, 15))
        default_surface.fill(GREEN)
        self.image = load_resource("gem.png", default_surface)
        self.image = pygame.transform.scale(self.image, (15, 15))
        self.rect = self.image.get_rect(center=self.rect.center)  # 更新 rect
        if random.random() < 0.2:
            item_type = random.choice(["speed", "multi"])
            items.add(Item(self.rect.centerx, self.rect.centery, item_type))

    def draw_hp(self, surface):
        if self.alive:
            text = self.font.render(str(self.hp), True, WHITE)
            surface.blit(text, (self.rect.x, self.rect.y - 20))

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
bullets = pygame.sprite.Group()
items = pygame.sprite.Group()

# 生成關卡
def setup_level(level):
    enemies.empty()
    bullets.empty()
    items.empty()
    for _ in range(5 + level * 2):
        x = random.randint(100, width - 100)
        y = random.randint(100, height - 100)
        enemies.add(Enemy(x, y, level))
    doors.empty()
    doors.add(Door(50, height // 2 - 50))
    doors.add(Door(width - 60, height // 2 - 50))

# 初始設定
level = 1
setup_level(level)
game_state = "start"
level_start_time = 0
level_time = 0

# 遊戲主迴圈
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "start":
                game_state = "playing"
                level_start_time = time.time()
                setup_level(level)
            elif game_state == "level_complete":
                game_state = "playing"
                level_start_time = time.time()
                setup_level(level)

    if game_state == "start":
        window.fill(BLACK)
        font = pygame.font.Font(None, 48)
        text = font.render("Click to Start", True, WHITE)
        window.blit(text, (width // 2 - 100, height // 2))
    elif game_state == "playing":
        player.update()
        enemies.update()
        bullets.update()
        items.update()
        # 自動發射子彈
        player.shoot(bullets)
        # 子彈與敵人碰撞
        for bullet in bullets:
            hit_enemies = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemy in hit_enemies:
                if enemy.alive:
                    enemy.take_damage(1)
                    bullet.kill()
        # 主角與寶石（非存活敵人）碰撞
        for enemy in enemies:
            if not enemy.alive and pygame.sprite.collide_rect(player, enemy):
                player.collect_gem(enemy)
        # 主角與道具碰撞
        hit_items = pygame.sprite.spritecollide(player, items, True)
        for item in hit_items:
            player.apply_item(item.type)
            if os.path.exists("item.wav"):
                sound = pygame.mixer.Sound("item.wav")
                sound.play()
        # 檢查關卡完成
        all_dead = all(not enemy.alive for enemy in enemies.sprites()) and not enemies
        if all_dead:
            level_time = time.time() - level_start_time
            for door in doors:
                door.closed = False
                door.image = pygame.Surface((0, 0))
            game_state = "level_complete"
            level += 1
        window.fill(BLACK)
        doors.draw(window)
        player_group.draw(window)
        enemies.draw(window)
        bullets.draw(window)
        items.draw(window)
        for enemy in enemies:
            enemy.draw_hp(window)
        font = pygame.font.Font(None, 36)
        attack_type = "Normal" if player.attack_type == 1 else "Fast" if player.attack_type == 2 else "Powerful"
        status_text = f"Level: {level} Gems: {player.gems} Attack: {attack_type} Time: {level_time:.1f}s"
        if player.item_effect == "speed":
            status_text += f" Speed Boost: {player.item_duration:.1f}s"
        elif player.item_effect == "multi":
            status_text += f" Multi-Shot: {player.item_duration:.1f}s"
        text = font.render(status_text, True, WHITE)
        window.blit(text, (10, 10))
    elif game_state == "level_complete":
        window.fill(BLACK)
        font = pygame.font.Font(None, 48)
        text = font.render(f"Level {level-1} Complete! Time: {level_time:.1f}s Click for Next Level", True, WHITE)
        window.blit(text, (width // 2 - 200, height // 2))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()