
class Level:
	def __init__( self, waypoints, waves ):
		self.waves = waves
		self.pauseTime = 15000
		self.level = waypoints
		self.lastWaveIndex = 0

class Wave:
	def __init__( self, enemyDropTime, maxEnemies, enemyHealthOffset, enemySpeedOffset, pointOffset ):
		self.enemyDropTime = enemyDropTime
		self.maxEnemies = maxEnemies
		self.enemyHealthOffset = enemyHealthOffset
		self.enemySpeedOffset = enemySpeedOffset
		self.pointOffset = pointOffset
