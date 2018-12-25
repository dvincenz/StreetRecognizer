import math


class SlicerConfig:
    def __init__(self, tileSize: int, baseOverlapFactor: float):
        self.tileSize = tileSize
        self.baseOverlapFactor = baseOverlapFactor
        self.x = DimensionConfig(
            tileSize=tileSize, baseOverlapFactor=baseOverlapFactor)
        self.y = DimensionConfig(
            tileSize=tileSize, baseOverlapFactor=baseOverlapFactor)

    def printDebugInformation(self, size: (int, int)):
        sizeX, sizeY = size
        numTilesX = self.x.getNumTiles(sizeX)
        numTilesY = self.y.getNumTiles(sizeY)
        print('X overlap: ' + self.x.getOverlapString(sizeX))
        print('Y overlap: ' + self.y.getOverlapString(sizeY))
        print('Expected Tiles: ' + str(numTilesX) + 'x' + str(numTilesY)
              + ' (' + str(numTilesX * numTilesY) + ')')
        print('The current settings produce the following error, due to rounding pixels per tile:')
        print('    X: ' + self.x.getRoundingErrorString(sizeX))
        print('    Y: ' + self.y.getRoundingErrorString(sizeY))


class DimensionConfig:
    def __init__(self, tileSize: int, baseOverlapFactor: float):
        self.tileSize = tileSize
        self.baseOverlap = tileSize * baseOverlapFactor

    def getNumTiles(self, size: int):
        return math.floor((size - self.baseOverlap) / (self.tileSize - self.baseOverlap) + 0.5)

    def getOverlapOffset(self, size: int):
        numTiles = self.getNumTiles(size)
        return math.ceil((size - numTiles * self.tileSize) / (1 - numTiles))

    def getOverlapString(self, size: int):
        return str(self.getOverlapOffset(size)) + " ({0:.2%})".format(self.getOverlapOffset(size) / self.tileSize)

    def getRoundingErrorString(self, size: int):
        numTiles = self.getNumTiles(size)
        overlapOffset = self.getOverlapOffset(size)
        actualSize = numTiles * (self.tileSize - overlapOffset) + overlapOffset
        if actualSize > size:
            return str(actualSize - size) + 'px of "black borders" ({0:.4%})'.format((actualSize - size) / size)

        if actualSize < size:
            return str(size - actualSize) + 'px missing ({0:.4%})'.format((size - actualSize) / size)

        return 'none!'
