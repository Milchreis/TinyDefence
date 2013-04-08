import pygame
from pygame.locals import *
import copy

import helpers
from tilemap import *
from level import *
from mobs import *

title = "TinyDefence"
version = 0.1

""" set up your own level """
# Syntax: [ Level( waypoints, waves ), Level( waypoints, waves )]
# waypoints: [ startpoint, toPoint, toPoint, ..., endPoint ]
# waves  [ Wave( spawningPause, numberOfEnemies, additionalHealth, additionalSpeed, additionalPoints ), ... ]

myLevel = [
	Level( 
			[[0, 3], [21, 3], [21, 5], [3,5], [3,7], [18, 7], [18, 9], [12, 9], [12, 12]],
			[ 	Wave( 1000, 1, 0, 0, 0.5 ), 
				Wave( 1000, 2, 0, 0, 0.5 ), 
				Wave( 1000, 5, 1, 1, 0.5 ), 
				Wave( 500, 2, 3, 0, 0.3 ), 
				Wave( 800, 10, 3, 2, 0.4 ), 
				Wave( 800, 15, 4, 3, 0.4 ), 
				Wave( 500, 20, 6, 3, 0.5 ), 
			] ),
 	Level(
			[[12, 0], [12, 5], [9, 5], [9, 9], [15, 9], [15, 14] ],
			[ 	Wave( 800,  8, 2, 1, 0.3 ), 
				Wave( 800, 10, 3, 2, 0.3 ), 
				Wave( 800,  6, 5, 1, 0.3 ), 
				Wave( 800,  8, 1, 3, 0.3 ), 
				Wave( 800, 15, 4, 1, 0.3 ), 
				Wave( 800, 20, 2, 3, 0.3 ), 
				Wave( 800, 3, 40, 1, 0.3 ), 
			] )
]
""" --------------------  """

class TowerDefenceGame:
	START = 0 
	GAME = 1
	WON = 2
	GAME_OVER = 3

	def __init__( self, width, height ):
		self.points = 15
		self.lifes = 5
		self.towers = []
		self.map = TileMap( width, height )
		self.levels = []
		self.levelIndex = 0
		self.enemies = []
		self.lastTick = 0
		self.state = TowerDefenceGame.START

	def reset( self ):
		self.towers = []
		self.points = 15
		self.lifes = 5
		self.map.reset()

	def addLevel( self, level ):
		self.levels.append( level )
		if( len( self.levels ) == 1 ):
			self.setLevel( self.levels[0] )

	def addTower( self, mousePos ):
		tile = self.map.getTileIndex( mousePos[0], mousePos[1] )

		# build tower on the way is not allowed
		if( self.map.getTileType( tile[0], tile[1] ) == TileMap.WAY ):
			return

		# calc pixel position (center of tile)
		tile[0] = tile[0] * self.map.tileWidth + self.map.tileWidth//2
		tile[1] = tile[1] * self.map.tileHeight + self.map.tileHeight//2

		tower = None
		for t in self.towers:
			if( t.x == tile[0] and t.y == tile[1] ):
				tower = t				

		if( tower == None ):
			tower = Tower( tile[0], tile[1] )

		if( self.points >= tower.price ):
			self.towers.append( Tower( tile[0], tile[1] ) )
			self.points -= tower.price 

	def setLevel( self, levelObj ):
		self.reset()
		lastPoint = levelObj.level[0]

		for point in levelObj.level:
			self.map.createStraightWay( lastPoint, point )
			lastPoint = point

		# set base on last point
		self.map.setBase( levelObj.level[-1] )

		self.lastTick = pygame.time.get_ticks()

	def render( self, screen ):

		if( self.state == TowerDefenceGame.GAME ):
			now = pygame.time.get_ticks()
			self.map.render( screen )

			level = self.levels[self.levelIndex]
			wave = level.waves[level.lastWaveIndex]
			if( now - self.lastTick > wave.enemyDropTime and wave.maxEnemies > 0 ): 
				enemy = Enemy( self.map.tileWidth, self.map.tileHeight )
				enemy.speed += wave.enemySpeedOffset
				enemy.health += wave.enemyHealthOffset
				enemy.currentHealth = enemy.health
				enemy.points += wave.pointOffset
				enemy.setWaypoints( level.level )
				self.enemies.append( enemy )

				wave.maxEnemies = wave.maxEnemies - 1
				self.lastTick = pygame.time.get_ticks()

			# check next event if all enemies down
			if( wave.maxEnemies == 0 and len( self.enemies ) == 0 ):
				# game won?
				if( self.levelIndex == len( self.levels )-1 and 
					level.lastWaveIndex == len( level.waves )-1 ):
					self.state = TowerDefenceGame.WON
				
				# next level?
				if( self.levelIndex < len( self.levels )-1 and 
					level.lastWaveIndex == len( level.waves )-1 ):
					self.levelIndex += 1
					self.setLevel( self.levels[self.levelIndex] )

				# next wave?
				if( level.lastWaveIndex != len( level.waves )-1  ):
					print( "pause is started" )
					if( now - self.lastTick > level.pauseTime ):
						print( "pause is over" )
						level.lastWaveIndex = level.lastWaveIndex + 1

			# check enemies
			toRemove = []
			for enemy in self.enemies:
				if( enemy.lastWaypointIndex == len( level.level ) - 1 ):
					toRemove.append( enemy )
					self.lifes -= 1

				if( enemy.currentHealth <= 0 ):
					toRemove.append( enemy )
					self.points += enemy.points

			for enemy in toRemove:
				self.enemies.remove( enemy )

			# render enemies
			for enemy in self.enemies:
				enemy.render( screen )

			# render towers and calc enemy and attacks
			mouse = pygame.mouse.get_pos()
			tile = [ mouse[0] // self.map.tileWidth, mouse[1] // self.map.tileHeight ]
			for tower in self.towers:
				if( tower.x // self.map.tileWidth == tile[0] and tower.y // self.map.tileHeight == tile[1] ):
					tower.isHover = True
				else:
					tower.isHover = False

				# look for an enemy in range
				if( tower.focusedEnemy == None ):
					for enemy in self.enemies:
						if( helpers.isInRange( tower, enemy ) ):
							tower.focusedEnemy = enemy
							break
				else:
					# is focused enemy already in range
					if( not helpers.isInRange( tower, tower.focusedEnemy ) 
						or tower.focusedEnemy.currentHealth <= 0):
						tower.focusedEnemy = None

				tower.render( screen )

			# render points and lifes
			myfont = pygame.font.SysFont( "sans", 20 )
			points = myfont.render( 'Points: ' + str( int( self.points ) ), 1, ( 255, 255, 0 ) )
			lifes = myfont.render( 'Lifes: ' + str( self.lifes ), 1, ( 255, 255, 0 ) )
			waves = myfont.render( 'Wave: ' + str( level.lastWaveIndex+1 ) + " of " +str( len( level.waves ) ), 1, ( 255, 255, 0 ) )
			screen.blit( points, ( 15, 10 ) )
			screen.blit( lifes, ( 15, 35 ) )
			screen.blit( waves, ( 15, 60 ) )

			if( self.lifes <= 0 ):
				self.state = TowerDefenceGame.GAME_OVER

			return

		if( self.state == TowerDefenceGame.START ):
			self.renderMenue( screen )
		
		if( self.state == TowerDefenceGame.WON ):
			self.renderWon( screen )

		if( self.state == TowerDefenceGame.GAME_OVER ):
			self.renderGameover( screen )


	def renderMenue( self, screen ):
		myfont = pygame.font.SysFont( "sans", 40 )
		txt = myfont.render( 'Click to start', 1, ( 255, 255, 255 ) )
		screen.blit( txt, ( 100, screen.get_height()//2 ) )

	def renderWon( self, screen ):
		print( "You won" )
		myfont = pygame.font.SysFont( "sans", 40 )
		txt = myfont.render( 'You won the game', 1, ( 255, 255, 255 ) )
		screen.blit( txt, ( 100, screen.get_height()//2 ) )

	def renderGameover( self, screen ):
		print( "You lose" )
		myfont = pygame.font.SysFont( "sans", 40 )
		txt = myfont.render( 'You loose the game', 1, ( 255, 255, 255 ) )
		screen.blit( txt, ( 100, screen.get_height()//2 ) )


def createGame( width, height, levels ):
	tdGame = TowerDefenceGame( width, height )
	tdGame.state = TowerDefenceGame.START

	for level in levels:
		tdGame.addLevel( copy.deepcopy( level ) )

	return tdGame

def main():
	pygame.init()
	screen = pygame.display.set_mode( ( 800, 576 ) )
	pygame.mouse.set_visible( 1 )

	pygame.key.set_repeat( 1, 30 )
	clock = pygame.time.Clock()

	tdGame = createGame( screen.get_width(), screen.get_height(), myLevel )

	running = True
	while running:
		clock.tick( 60 )
		screen.fill( ( 0, 0, 0 ) )

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					pygame.event.post( pygame.event.Event( pygame.QUIT ) )

			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					if( tdGame.state == TowerDefenceGame.START ):
						tdGame.state = TowerDefenceGame.GAME

					elif( tdGame.state == TowerDefenceGame.GAME_OVER or tdGame.state == TowerDefenceGame.WON ):
						tdGame = createGame( screen.get_width(), screen.get_height(), myLevel )
					else:
						tdGame.addTower( event.pos )

		# render game
		tdGame.render( screen )

		# show fps in window title
		pygame.display.set_caption( title + " - FPS: %.1f" % clock.get_fps() )
		pygame.display.flip()

	# exit
	pygame.quit()

if __name__ == '__main__':
	main()