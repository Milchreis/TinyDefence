import pygame
from pygame.gfxdraw import *
from pygame.locals import *
import math

title = "TinyDefence"
version = 0.1

WIDTH = 800
HEIGHT = 576

def isInRange( tower, enemy ):
	x = ( enemy.x - tower.x ) * ( enemy.x - tower.x )
	y = ( enemy.y - tower.y ) * ( enemy.y - tower.y )
	return math.sqrt( x + y ) < tower.range + enemy.radius

class Level:
	def __init__( self ):
		self.waves = []
		self.pauseTime = 15000
		self.level = []
		self.lastWaveIndex = 0

class FirstLevel( Level ):
	def __init__( self ):
		Level.__init__( self )
		# path points for the map and the enemies
		self.level = [ [0, 3], [21, 3], [21, 5], [3,5], [3,7], [18, 7],
				[18, 9], [12, 9], [12, 12] 
			]

		# enemyDropTime, maxEnemies, enemyHealthOffset, enemySpeedOffset, pointOffset
		self.waves.append( Wave( 1000, 5, 0, 0, 0.2 ) )
		self.waves.append( Wave( 1000, 10, 1, 1, 0.2 ) )
		self.waves.append( Wave( 950, 10, 2, 2, 0.2 ) )
		self.waves.append( Wave( 850, 5, 5, 3, 0.2 ) )
		self.waves.append( Wave( 500, 10, 1, 2, 0.4 ) )
		self.waves.append( Wave( 700, 20, 1, 5, 0.4 ) )
		self.waves.append( Wave( 1000, 1, 30, 0, 10 ) )

class TowerDefenceGame:
	START = 0 
	GAME = 1
	WON = 2
	GAME_OVER = 3

	def __init__( self ):
		self.points = 15
		self.lifes = 5
		self.towers = []
		self.map = TileMap()
		self.level = FirstLevel()
		self.setLevel( self.level )
		self.enemies = []
		self.lastTick = 0
		self.state = TowerDefenceGame.START

	def addTower( self, mousePos ):
		tile = self.map.getTileIndex( mousePos[0], mousePos[1] )

		# normalize to grid
		#tileX = ( mousePos[0] // self.map.tileWidth )
		#tileY = ( mousePos[1] // self.map.tileHeight )

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

			wave = self.level.waves[self.level.lastWaveIndex]
			if( now - self.lastTick > wave.enemyDropTime and wave.maxEnemies > 0 ): 
				enemy = Enemy( self.map.tileWidth, self.map.tileHeight )
				enemy.speed += wave.enemySpeedOffset
				enemy.health += wave.enemyHealthOffset
				enemy.currentHealth = enemy.health
				enemy.points += wave.pointOffset
				enemy.setWaypoints( self.level.level )
				self.enemies.append( enemy )

				wave.maxEnemies = wave.maxEnemies - 1
				self.lastTick = pygame.time.get_ticks()

			if( wave.maxEnemies == 0 and len( self.enemies ) == 0 ):
				if( self.level.lastWaveIndex == len( self.level.waves )-1 ):
					self.state = TowerDefenceGame.WON
				else:
					print( "pause is started" )
					if( now - self.lastTick > self.level.pauseTime ):
						print( "pause is over" )
						self.level.lastWaveIndex = self.level.lastWaveIndex + 1

			# check enemies
			toRemove = []
			for enemy in self.enemies:
				if( enemy.lastWaypointIndex == len( self.level.level ) - 1 ):
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
						if( isInRange( tower, enemy ) ):
							tower.focusedEnemy = enemy
							break
				else:
					# is focused enemy already in range
					if( not isInRange( tower, tower.focusedEnemy ) 
						or tower.focusedEnemy.currentHealth <= 0):
						tower.focusedEnemy = None

				tower.render( screen )

			# render points and lifes
			myfont = pygame.font.SysFont( "sans", 20 )
			points = myfont.render( 'Points: ' + str( int( self.points ) ), 1, ( 255, 255, 0 ) )
			lifes = myfont.render( 'Lifes: ' + str( self.lifes ), 1, ( 255, 255, 0 ) )
			waves = myfont.render( 'Wave: ' + str( self.level.lastWaveIndex+1 ) + " of " +str( len( self.level.waves ) ), 1, ( 255, 255, 0 ) )
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
		screen.blit( txt, ( 100, HEIGHT//2 ) )

	def renderWon( self, screen ):
		print( "You won" )
		myfont = pygame.font.SysFont( "sans", 40 )
		txt = myfont.render( 'You won the game', 1, ( 255, 255, 255 ) )
		screen.blit( txt, ( 100, HEIGHT//2 ) )

	def renderGameover( self, screen ):
		print( "You lose" )
		myfont = pygame.font.SysFont( "sans", 40 )
		txt = myfont.render( 'You loose the game', 1, ( 255, 255, 255 ) )
		screen.blit( txt, ( 100, HEIGHT//2 ) )

class TileMap:
	PLAIN = 0
	WAY = 1
	BASE = 2

	PLAIN_COLOR = ( 71, 161, 71 )
	WAY_COLOR = ( 174, 149, 89 )
	BASE_COLOR = ( 10, 10, 10 )

	def __init__( self ):
		self.tileWidth = 32
		self.tileHeight = 32
		self.mapWidth = WIDTH // self.tileWidth
		self.mapHeight = HEIGHT // self.tileHeight
		self.map = []

		self.base = []

		# create plain map
		for x in xrange( self.mapWidth ):
			self.map.append( [] )
			for y in xrange( self.mapHeight ):
				self.map[x].append( TileMap.PLAIN )

	def getTileIndex( self, x, y ):
		return [ x // self.tileWidth, y // self.tileHeight ]

	def getTileType( self, tileX, tileY ):
		return self.map[tileX][tileY]

	def setBase( self, tile ):
		self.base = tile
		self.map[tile[0]][tile[1]] = TileMap.BASE

	def render( self, screen ):
		for x in xrange( self.mapWidth ):
			for y in xrange( self.mapHeight ):
				tiletype = self.map[x][y] 
				color = None

				if( tiletype == TileMap.PLAIN ):
					color = TileMap.PLAIN_COLOR
				
				if( tiletype == TileMap.WAY ):
					color = TileMap.WAY_COLOR

				if( tiletype == TileMap.BASE ):
					color = TileMap.BASE_COLOR
				
				# tile bg
				pygame.draw.rect( screen, color, (x*self.tileWidth, y*self.tileHeight, self.tileWidth, self.tileHeight), 0 )
				
				# tile border
				pygame.draw.rect( screen, (133, 180, 133), (x*self.tileWidth, y*self.tileHeight, self.tileWidth, self.tileHeight), 1 )

	def createStraightWay( self, fromPosition, toPosition ):
		""" please, use only straight lines """
		
		start = None
		end = None
		isX = None

		if( fromPosition[0] == toPosition[0] ):
			isX = True
			start = fromPosition[1]
			end = toPosition[1]
		else:
			isX = False
			start = fromPosition[0]
			end = toPosition[0]

		if( start > end ):
			start, end = end, start

		for i in range( start, end+1, 1 ):
			if( isX ):
				self.map[fromPosition[0]][i] = TileMap.WAY
			else:
				self.map[i][fromPosition[1]] = TileMap.WAY

class Wave:
	def __init__( self, enemyDropTime, maxEnemies, enemyHealthOffset, enemySpeedOffset, pointOffset ):
		self.enemyDropTime = enemyDropTime
		self.maxEnemies = maxEnemies
		self.enemyHealthOffset = enemyHealthOffset
		self.enemySpeedOffset = enemySpeedOffset
		self.pointOffset = pointOffset

class Tower:
	def __init__( self, x, y ):
		self.x = x
		self.y = y
		self.radius = 10
		self.strange = 2.0
		self.range = 60
		self.price = 5
		self.focusedEnemy = None
		self.attackPause = 800
		self.isHover = False
		
		self.attacks = []
		self.attackTicks = 3
		self.attackTicksCount = 0
		self.lastTick = 0
		self.attackPos = None

	def render( self, screen ):
		now = pygame.time.get_ticks()
		pygame.draw.circle( screen, (0, 0, 200), (self.x, self.y), self.radius )

		if( self.isHover ):
			pygame.draw.circle( screen, (200, 200, 200, 200), (self.x, self.y), self.range, 1 )

		if( self.focusedEnemy != None and ( now - self.lastTick ) >= self.attackPause ):
			self.attacks.append( Attack( self ) )
			self.lastTick = pygame.time.get_ticks()

		toRemove = []
		for a in self.attacks:
			if( a.isOver ):
				toRemove.append( a )

		for a in toRemove:
			self.attacks.remove( a )

		for a in self.attacks:
			a.render( screen, self.focusedEnemy )


class Attack:
	def __init__( self, tower ):
		self.tower = tower
		self.attackTicks = 5
		self.attackTicksCount = 0
		self.lastTick = 0
		self.enemy = None
		self.isOver = False

	def render( self, screen, enemy ):
		self.enemy = enemy
		now = pygame.time.get_ticks()

		if( enemy != None and isInRange( self.tower, enemy ) ):
			dx = enemy.x - self.tower.x
			dy = enemy.y - self.tower.y
			steps = dx // self.attackTicks
			
			if( dx == 0 ):
				dx = 0.01

			a = self.tower.x - ( self.tower.x + ( steps*self.attackTicksCount ) )
			b = (a * dy) / dx
			attackPos = [int( self.tower.x - a ), int( self.tower.y - b ) ]

			if( self.attackTicksCount <= self.attackTicks ):
				pygame.draw.circle( screen, (20, 20, 20), (attackPos[0], attackPos[1] ), 3 )
				self.attackTicksCount += 1
			else:
				enemy.currentHealth -= self.tower.strange
				self.isOver = True
		else:
			self.isOver = True

class Enemy:
	def __init__( self, tileWidth, tileHeight ):
		self.x = 100
		self.y = 100
		self.waypoints = []
		self.speed = 1
		self.health = 10.0
		self.currentHealth = self.health
		self.points = 0.5
		self.tileWidth = tileWidth
		self.tileHeight = tileHeight
		self.radius = 10
		self.lastWaypointIndex = 0

	def setWaypoints( self, waypoints ):
		self.waypoints = waypoints
		self.x = self.waypoints[0][0] * (self.tileWidth) + (self.tileWidth//2)
		self.y = self.waypoints[0][1] * (self.tileHeight) + (self.tileHeight//2) 

	def isAround( self, valueA, valueB, range ):
		if( valueA >= valueB-range and valueA < valueB+range ):
			return True
		else:
			return False

	def render( self, screen ):
		nextWaypoint = self.waypoints[self.lastWaypointIndex+1]
		nextWaypoint = [
				nextWaypoint[0]*(self.tileWidth)+(self.tileWidth//2), 
				nextWaypoint[1]*(self.tileHeight)+(self.tileHeight//2) 
			]

		if( self.isAround( self.x, nextWaypoint[0], 5 ) and
			self.isAround( self.y, nextWaypoint[1], 5 ) ):
			self.lastWaypointIndex = self.lastWaypointIndex+1

		if( self.x < nextWaypoint[0] ):
			if( self.x + self.speed > nextWaypoint[0] ):
				self.x = nextWaypoint[0]
			else:
				self.x = self.x + self.speed

		if( self.x > nextWaypoint[0] ):
			if( self.x - self.speed < nextWaypoint[0] ):
				self.x = nextWaypoint[0]
			else:
				self.x = self.x - self.speed

		if( self.y < nextWaypoint[1] ):
			if( self.y + self.speed > nextWaypoint[1] ):
				self.y = nextWaypoint[1]
			else:
				self.y = self.y + self.speed

		if( self.y > nextWaypoint[1] ):
			if( self.y - self.speed < nextWaypoint[1] ):
				self.y = nextWaypoint[1]
			else:
				self.y = self.y - self.speed

		pygame.draw.circle( screen, (200, 0, 0), (self.x, self.y), self.radius )

		# render health
		width = (self.currentHealth/self.health) * 30
		pygame.draw.rect( screen, (255,0,0), (self.x-15, self.y+15, 30, 2 ), 0 )
		pygame.draw.rect( screen, (0,255,0), (self.x-15, self.y+15, int( width ), 2 ), 0 )

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    pygame.mouse.set_visible(1)
    pygame.key.set_repeat(1, 30)

    clock = pygame.time.Clock()
    tdGame = TowerDefenceGame()

    running = True
    while running:
        clock.tick(60)
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                	if( tdGame.state == TowerDefenceGame.START ):
                		tdGame.state = TowerDefenceGame.GAME
                	else:
                		tdGame.addTower( event.pos )

        # render game
        tdGame.render( screen )

        # show fps in window title
        pygame.display.set_caption( title + " - FPS: %.1f" % clock.get_fps() )
        pygame.display.flip()

if __name__ == '__main__':
    main()