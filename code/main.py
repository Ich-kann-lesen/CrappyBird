import pygame, sys, time
from random import randint

"""
TO DO:



"""

WIDTH = 480
HEIGHT = 800
FRAMERATE = 60

class BG(pygame.sprite.Sprite):
	def __init__(self,groups,scale_factor):
		super().__init__(groups)
		bg_image = pygame.image.load('..\\graphics\\environment\\background.png').convert()

		full_height = bg_image.get_height() * scale_factor
		full_width = bg_image.get_width() * scale_factor
		full_sized_image = pygame.transform.scale(bg_image,(full_width,full_height))
		
		self.image = pygame.Surface((full_width * 2,full_height))
		self.image.blit(full_sized_image,(0,0))
		self.image.blit(full_sized_image,(full_width,0))

		self.rect = self.image.get_rect(topleft = (0,0))
		self.pos = pygame.math.Vector2(self.rect.topleft)

	def update(self,dt):
		self.pos.x -= 300 * dt
		if self.rect.centerx <= 0:
			self.pos.x = 0
		self.rect.x = round(self.pos.x)

class Ground(pygame.sprite.Sprite):
	def __init__(self,groups,scale_factor):
		super().__init__(groups)
		self.sprite_type = 'ground'
		
		# image
		ground_surf = pygame.image.load('..\\graphics\\environment\\ground.png').convert_alpha()
		self.image = pygame.transform.scale(ground_surf,(pygame.math.Vector2(ground_surf.get_size()) * scale_factor) / 5)
		
		# position
		self.rect = self.image.get_rect(bottomleft = (0,HEIGHT))
		self.pos = pygame.math.Vector2(self.rect.topleft)

		# mask
		self.mask = pygame.mask.from_surface(self.image)

	def update(self,dt):
		self.pos.x -= 360 * dt
		if self.rect.centerx <= 0:
			self.pos.x = 0

		self.rect.x = round(self.pos.x)

class Bird(pygame.sprite.Sprite):
	def __init__(self,groups,scale_factor):
		super().__init__(groups)

		# image 
		self.import_frames(scale_factor)
		self.frame_index = 0
		self.image = self.frames[self.frame_index]

		# rect
		self.rect = self.image.get_rect(midleft = (WIDTH / 20,HEIGHT / 2))
		self.pos = pygame.math.Vector2(self.rect.topleft)

		# movement
		self.gravity = 900
		self.direction = 0

		# mask
		self.mask = pygame.mask.from_surface(self.image)

	def import_frames(self,scale_factor):
		self.frames = []
		for i in range(2):
			surf = pygame.image.load(f'..\\graphics\\bird\\FlappyBird{i}.png').convert_alpha()
			scaled_surface = pygame.transform.scale(surf,pygame.math.Vector2(surf.get_size())* scale_factor / 20)
			self.frames.append(scaled_surface)

	def apply_gravity(self,dt):
		self.direction += self.gravity * dt
		self.pos.y += self.direction * dt
		self.rect.y = round(self.pos.y)

	def jump(self):
		self.direction = -400

	def animate(self,dt):
		self.frame_index += 10 * dt
		if self.frame_index >= len(self.frames):
			self.frame_index = 0
		self.image = self.frames[int(self.frame_index)]

	def rotate(self):
		rotated_bird = pygame.transform.rotozoom(self.image,-self.direction * 0.06,1)
		self.image = rotated_bird
		self.mask = pygame.mask.from_surface(self.image)

	def update(self,dt):
		self.apply_gravity(dt)
		self.animate(dt)
		self.rotate()

class Obstacle(pygame.sprite.Sprite):
	def __init__(self,groups,scale_factor, isBottom, pipeHight):
		super().__init__(groups)
		self.sprite_type = 'obstacle'
		surf = pygame.image.load(f'..\\graphics\\obstacles\\Pipe.png').convert_alpha()
		self.image = pygame.transform.scale(surf,(pygame.math.Vector2(surf.get_size()) * scale_factor) / 10)
		self.isBottom = isBottom
		self.pipeHight = pipeHight
		
		x = WIDTH

		if self.isBottom:
			self.rect = self.image.get_rect(midtop = (x,self.pipeHight + 100))
		else:
			self.image = pygame.transform.flip(self.image,False,True)
			self.rect = self.image.get_rect(midbottom = (x,self.pipeHight - 100))

		self.pos = pygame.math.Vector2(self.rect.topleft)

		# mask
		self.mask = pygame.mask.from_surface(self.image)

	def update(self,dt):
		self.pos.x -= 400 * dt
		self.rect.x = round(self.pos.x)
		if self.rect.right <= -100:
			self.kill()

class Game:
	def __init__(self):
		
		# setup
		pygame.init()
		self.display_surface = pygame.display.set_mode((WIDTH,HEIGHT))
		pygame.display.set_caption('Crappy Bird')
		self.clock = pygame.time.Clock()
		self.active = True

		# sprite groups
		self.all_sprites = pygame.sprite.Group()
		self.collision_sprites = pygame.sprite.Group()

		# scale factor
		bg_height = pygame.image.load('..\\graphics\\environment\\background.png').get_height()
		self.scale_factor = HEIGHT / bg_height

		# sprite setup 
		BG(self.all_sprites,self.scale_factor)
		Ground([self.all_sprites,self.collision_sprites],self.scale_factor)
		self.bird = Bird(self.all_sprites,self.scale_factor / 1.7)

		# timer
		self.obstacle_timer = pygame.USEREVENT + 1
		pygame.time.set_timer(self.obstacle_timer,1400)

		# text
		self.font = pygame.font.Font('..\\graphics\\font\\BD_Cartoon_Shout.ttf',30)
		self.score = 0
		self.start_offset = 0

		# menu
		self.menu_surf = pygame.image.load('..\\graphics\\ui\\menu.png').convert_alpha()
		self.menu_rect = self.menu_surf.get_rect(center = (WIDTH / 2,HEIGHT / 2))


	def collisions(self):
		if pygame.sprite.spritecollide(self.bird,self.collision_sprites,False,pygame.sprite.collide_mask)\
		or self.bird.rect.top <= 0:
			for sprite in self.collision_sprites.sprites():
				if sprite.sprite_type == 'obstacle':
					sprite.kill()
			self.active = False
			self.bird.kill()

	def display_score(self):
		score = str(self.score)
		if self.active:
			self.score = (pygame.time.get_ticks() - self.start_offset) // 1000
			y = HEIGHT / 10
		else:
			score += " # " + score_string[2:]
			y = HEIGHT / 2 + (self.menu_rect.height / 1.5)

		score_surf = self.font.render(score,True,'black')
		score_rect = score_surf.get_rect(midtop = (WIDTH / 2,y))
		self.display_surface.blit(score_surf,score_rect)

	def write_score(self):
		if last_active:
			global score_string
			file_a = open("..\\scores\\scores.txt", "a")
			file_r = open("..\\scores\\scores.txt", "r")
			score_string = file_r.read()

			score_list = []
			n = ""
			for c in score_string:
				if c == "\n":
					score_list.append(int(float(n)))
					n = ""
				else:
					n += c
			score_list = sorted(score_list, reverse=True)
			score_string = ""
			for x in score_list[:5]:
				score_string += ", " + str(x)

			print(score_string)
			file_a.write(str(self.score) + "\n")

	def run(self):
		last_time = time.time()
		while True:
			# delta time
			dt = time.time() - last_time
			last_time = time.time()

			global last_active
			last_active = self.active

			# event loop
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()

				if event.type == pygame.KEYDOWN:
					if self.active:
						self.bird.jump()
					else:
						self.bird = Bird(self.all_sprites,self.scale_factor / 1.7)
						self.active = True
						self.start_offset = pygame.time.get_ticks()

				if event.type == self.obstacle_timer and self.active:
					pipeHight = HEIGHT / 2 + randint(-200, 200)
					Obstacle([self.all_sprites,self.collision_sprites],self.scale_factor * 1.1, True, pipeHight)
					Obstacle([self.all_sprites,self.collision_sprites],self.scale_factor * 1.1, False, pipeHight)
			
			# game logic
			self.all_sprites.update(dt)
			self.all_sprites.draw(self.display_surface)
			self.display_score()

			if self.active:
				self.collisions()
			if not self.active:
				self.display_surface.blit(self.menu_surf,self.menu_rect)
				self.write_score()

			pygame.display.update()
			self.clock.tick(FRAMERATE)

if __name__ == '__main__':
	game = Game()
	game.run()






