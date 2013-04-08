import math

def isInRange( tower, enemy ):
	x = ( enemy.x - tower.x ) * ( enemy.x - tower.x )
	y = ( enemy.y - tower.y ) * ( enemy.y - tower.y )
	return math.sqrt( x + y ) < tower.range + enemy.radius

""" enemy, tower """
def getPoint( p1, p2, x ):
	dx = p1[0] - p2[0]
	dy = p1[1] - p2[1]
	
	if( dx == 0 ): dx = 0.01

	a = p2[0] - ( p2[0] + x )
	b = (a * dy) / dx
	return [int( p2[0] - a ), int( p2[1] - b ) ]