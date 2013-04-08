import pygame

class TileMap:
	PLAIN = 0
	WAY = 1
	BASE = 2

	PLAIN_COLOR = ( 71, 161, 71 )
	WAY_COLOR = ( 174, 149, 89 )
	BASE_COLOR = ( 10, 10, 10 )

	def __init__( self, width, height ):
		self.tileWidth = 32
		self.tileHeight = 32
		self.mapWidth = width // self.tileWidth
		self.mapHeight = height // self.tileHeight
		self.map = []

		self.base = []
		
		# create plain map
		for x in xrange( self.mapWidth ):
			self.map.append( [] )
			for y in xrange( self.mapHeight ):
				self.map[x].append( TileMap.PLAIN )


	def reset( self ):
		for x in xrange( self.mapWidth ):
			for y in xrange( self.mapHeight ):
				self.map[x][y] = TileMap.PLAIN

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