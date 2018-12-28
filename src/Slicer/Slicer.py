import json
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
        self.image = Image.open(os.path.join(imagePath, imageName))

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

    def saveTiles(self, tiles: [Tile], config: SlicerConfig, outPath: str, removeExisting=True):
        print('saving... (to ' + os.path.abspath(outPath) + ')')

        outDir = os.path.join(outPath, os.path.splitext(self.imageName)[0])

        if removeExisting and os.path.exists(outDir):
            shutil.rmtree(outDir, ignore_errors=True)

        os.makedirs(outDir, exist_ok=True)

        sizeX, sizeY = self.image.size

        data = {}
        data['imageName'] = self.imageName
        data['imageSize'] = {
            'width': sizeX,
            'height': sizeY
        }
        data['wgs84'] = {
            'top': 0,
            'left': 0,
            'bottom': 0,
            'right': 0
        }
        data['tileConfig'] = {
            'tileSize': config.tileSize,
            'overlapPixelsX': config.x.getOverlapOffset(sizeX),
            'overlapPixelsY': config.y.getOverlapOffset(sizeY),
            'overlapFactorX': config.x.getOverlapOffset(sizeX) / config.tileSize,
            'overlapFactorY': config.y.getOverlapOffset(sizeY) / config.tileSize,
            'numTilesX': config.x.getNumTiles(sizeX),
            'numTilesY': config.y.getNumTiles(sizeY)
        }
        data['tileDirectory'] = os.path.splitext(self.imageName)[0]
        data['tiles'] = []

        for i, tile in enumerate(tiles):
            tileName = "{:0>3d},{:0>3d}.png".format(tile.top, tile.left)
            tile.image.save(os.path.join(outDir, tileName), "PNG")

            data['tiles'].append({
                'tileName': tileName,
                'pixels': {
                    'top': tile.top,
                    'left': tile.left,
                    'bottom': tile.bottom,
                    'right': tile.right
                },
                'wgs84': {
                    'top': 0,
                    'left': 0,
                    'bottom': 0,
                    'right': 0
                }
            })

            if (i+1) % 50 == 0:
                print('  {0:d}/{1:d} ({2:.1%})'.format((i+1),
                                                       len(tiles), (i+1) / len(tiles)))

        with open(outDir + '.json', 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=4)
