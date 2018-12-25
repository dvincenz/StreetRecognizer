import math
import os
import shutil

from PIL import Image

from SlicerConfig import SlicerConfig


class Tile:
    def __init__(self, image: Image, coords: ((int, int), (int, int))):
        self.image = image
        topLeft, bottomRight = coords
        self.left, self.top = topLeft
        self.right, self.bottom = bottomRight


class Slicer:
    def __init__(self, imagePath: str, imageName: str):
        self.imageName = imageName
        self.image = Image.open(imagePath + imageName)

    def slice(self, config: SlicerConfig):
        print('slicing...')

        sizeX, sizeY = self.image.size
        stepX = config.tileSize - config.x.getOverlapOffset(sizeX)
        stepY = config.tileSize - config.y.getOverlapOffset(sizeY)
        maxX = sizeX - math.floor(config.tileSize / 2)
        maxY = sizeY - math.floor(config.tileSize / 2)
        maxTiles = math.ceil(maxX / stepX) * math.ceil(maxY / stepY)

        tiles = []
        for x in range(0, maxX, stepX):
            for y in range(0, maxY, stepY):
                left = x
                top = y
                right = left + config.tileSize
                bottom = top + config.tileSize
                tileImage = self.image.crop((left, top, right, bottom))
                tile = Tile(image=tileImage, coords=(
                    (left, top), (right, bottom)))
                tiles.append(tile)

                if len(tiles) % 50 == 0:
                    print('  {0:d}/{1:d} ({2:.1%})'.format(len(tiles),
                                                           maxTiles, len(tiles) / maxTiles))
        return tiles

    def saveTiles(self, tiles: [Tile], outPath: str, removeExisting=True):
        print('saving...')

        outDir = outPath + self.imageName

        if removeExisting and os.path.exists(outDir):
            shutil.rmtree(outDir, ignore_errors=True)

        os.makedirs(outDir, exist_ok=True)

        for i, tile in enumerate(tiles):
            tileName = "{}/{:0>3d},{:0>3d}.png".format(
                outDir, tile.top, tile.left)
            tile.image.save(tileName, "PNG")

            if (i+1) % 50 == 0:
                print('  {0:d}/{1:d} ({2:.1%})'.format((i+1),
                                                       len(tiles), (i+1) / len(tiles)))
