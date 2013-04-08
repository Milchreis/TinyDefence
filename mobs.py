import pygame
import helpers

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
		self.attackPos = [x+10, y+10]
		self.attacks = []
		self.lastTick = 0

	def render( self, screen ):
		now = pygame.time.get_ticks()
		pygame.draw.circle( screen, (0, 0, 200), (self.x, self.y), self.radius )
		#pygame.draw.line( screen, (0,0,0), (self.x, self.y), (self.attackPos[0], self.attackPos[1]), 3 ) 

		if( self.isHover ):
			pygame.draw.circle( screen, (200, 200, 200, 200), (self.x, self.y), self.range, 1 )

		if( self.focusedEnemy != None ):
			# TODO: calc barrel direction
			dx = self.focusedEnemy.x - self.x
			#self.attackPos = helpers.getPoint( ( self.focusedEnemy.x, self.focusedEnemy.y ), 
			#								   ( self.x, self.y), 5 )

			if( ( now - self.lastTick ) >= self.attackPause ):
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

		if( enemy != None and helpers.isInRange( self.tower, enemy ) ):
			dx = enemy.x - self.tower.x
			x = ( dx // self.attackTicks ) * self.attackTicksCount
			attackPos = helpers.getPoint( ( enemy.x, enemy.y ), ( self.tower.x, self.tower.y), x )

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