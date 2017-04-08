import pygame
import random

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 500
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PURPLE = (155, 89, 182)
YELLOW = (237, 194, 51)
PLAYER_SPEED = 7 # pixel per frame
ENEMY_SPEED = 5


class Game:

	def __init__(self, screen):
		self.screen = screen
		self.started = False
		self.game_over = False
		coin_pickup = pygame.mixer.Sound("coin_pickup.wav")
		coin_pickup.set_volume(0.3)
		self.sounds = {
			"coin pickup":coin_pickup,
			"lose":pygame.mixer.Sound("lose.wav")
		}
		self.score = 0
		self.best = 0
		self.all_sprites = pygame.sprite.Group()
		self.walls = pygame.sprite.Group()
		self.enemies = pygame.sprite.Group()
		self.coins = pygame.sprite.Group()
		self.create_objects()
		self.enemy_respawn_event = pygame.USEREVENT+1
		pygame.time.set_timer(self.enemy_respawn_event, 750)

	def create_objects(self):
		self.create_walls()
		self.player = Player(330, 230)
		self.player.walls = self.walls
		self.all_sprites.add(self.player)
		self.create_coin()

	def create_walls(self):
		wall_1 = Wall(200, 150, 10, 200)
		self.walls.add(wall_1)
		self.all_sprites.add(wall_1)

		wall_2 = Wall(200, 350, 310, 10)
		self.walls.add(wall_2)
		self.all_sprites.add(wall_2)

		wall_3 = Wall(500, 150, 10, 200)
		self.walls.add(wall_3)
		self.all_sprites.add(wall_3)
		
		wall_4 = Wall(200, 150, 310, 10)
		self.walls.add(wall_4)
		self.all_sprites.add(wall_4)

	def create_coin(self):
		x_pos = random.randint(230, 470)
		y_pos = random.randint(180, 310)
		self.coin = Coin(x_pos, y_pos)
		self.all_sprites.add(self.coin)
		self.coins.add(self.coin)

	def create_enemy(self):
		_dir = random.choice(["U", "D", "L", "R"])
		x_speed, y_speed = 0, 0
		if _dir == "U":
			x_pos = random.randint(230, 470)
			y_pos = SCREEN_HEIGHT - 20
			y_speed = -ENEMY_SPEED
		elif _dir == "D":
			x_pos = random.randint(230, 470)
			y_pos = 20
			y_speed = ENEMY_SPEED
		elif _dir == "L":
			y_pos = random.randint(170, 320)
			x_pos = SCREEN_WIDTH - 20
			x_speed = -ENEMY_SPEED
		elif _dir == "R":
			y_pos = random.randint(170, 320)
			x_pos = 20
			x_speed = ENEMY_SPEED
		enemy = Enemy(x_pos, y_pos, x_speed, y_speed)
		self.all_sprites.add(enemy)
		self.enemies.add(enemy)

	def run(self):
		clock = pygame.time.Clock()
		while not self.game_over:
			self.process_events()
			self.run_logic()
			self.display_frame()
			clock.tick(60)

	def process_events(self):
		for event in pygame.event.get():
			if self.started:
				if event.type == self.enemy_respawn_event:
					self.create_enemy()

			if event.type == pygame.QUIT:
				self.game_over = True

			elif event.type == pygame.KEYDOWN:
				self.started = True
				if event.key == pygame.K_LEFT:
					self.player.change_speed(-PLAYER_SPEED, 0)
				elif event.key == pygame.K_RIGHT:
					self.player.change_speed(PLAYER_SPEED, 0)
				elif event.key == pygame.K_UP:
					self.player.change_speed(0, -PLAYER_SPEED)
				elif event.key == pygame.K_DOWN:
					self.player.change_speed(0, PLAYER_SPEED)

			elif event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT:
					self.player.change_speed(PLAYER_SPEED, 0)
				elif event.key == pygame.K_RIGHT:
					self.player.change_speed(-PLAYER_SPEED, 0)
				elif event.key == pygame.K_UP:
					self.player.change_speed(0, PLAYER_SPEED)
				elif event.key == pygame.K_DOWN:
					self.player.change_speed(0, -PLAYER_SPEED)
			

	def run_logic(self):
		if not self.game_over:
			self.all_sprites.update()
		player_coin_collide = pygame.sprite.spritecollide(self.player, self.coins, True)
		if player_coin_collide:
			self.score += 1
			self.sounds["coin pickup"].play()
			self.create_coin()
		player_enemy_collide = pygame.sprite.spritecollide(self.player, self.enemies, True)
		if player_enemy_collide:
			if self.score > self.best:
				self.best = self.score
			self.score = 0
			self.sounds["lose"].play()

	def display_frame(self):
		screen.fill(PURPLE)
		if not self.game_over:
			font = pygame.font.SysFont("Arial", 20)
			score = font.render("score: " + str(self.score), True, WHITE)
			best = font.render("best: " + str(self.best), True, WHITE)
			self.screen.blit(score, (30, 30))
			self.screen.blit(best, (30, 50))
			if not self.started:
				i = "Use arrow keys to take the coin"
				instructions = font.render(i, True, WHITE)
				self.screen.blit(instructions, (200, 80))
			self.all_sprites.draw(self.screen)
		pygame.display.flip()


class Player(pygame.sprite.Sprite):

	def __init__(self, x, y):
		self.image = pygame.Surface([50, 50])
		self.image.fill(WHITE)
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.x_speed = 0
		self.y_speed = 0
		self.walls = None
		super().__init__()

	def change_speed(self, x, y):
		self.x_speed += x
		self.y_speed += y

	def update(self):
		self.rect.x += self.x_speed
		walls_hit = pygame.sprite.spritecollide(self, self.walls, False)
		for wall in walls_hit:
			if self.x_speed > 0:
				self.rect.right = wall.rect.left
			else:
				self.rect.left = wall.rect.right

		self.rect.y += self.y_speed
		walls_hit = pygame.sprite.spritecollide(self, self.walls, False)
		for wall in walls_hit:
			if self.y_speed > 0:
				self.rect.bottom = wall.rect.top
			else:
				self.rect.top = wall.rect.bottom

class Coin(pygame.sprite.Sprite):

	def __init__(self, x, y):
		self.image = pygame.Surface([30, 30])
		self.image.fill(PURPLE)
		pygame.draw.circle(self.image, YELLOW, (15, 15), 15)
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		super().__init__()


class Enemy(pygame.sprite.Sprite):

	def __init__(self, x, y, x_speed, y_speed):
		self.image = pygame.Surface([20, 20])
		self.image.fill(BLACK)
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.x_speed = x_speed
		self.y_speed = y_speed
		super().__init__()

	def update(self):
		self.rect.x += self.x_speed
		self.rect.y += self.y_speed


class Wall(pygame.sprite.Sprite):

	def __init__(self, x, y, width, height):
		self.image = pygame.Surface([width, height])
		self.image.fill(WHITE)
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		super().__init__()


if __name__ == '__main__':
	pygame.init()
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	pygame.display.set_caption("PGSQR")
	game = Game(screen)
	game.run()
	pygame.quit()