from PIL import Image
from contextlib import contextmanager
from crowdcount.models import density_map
from crowdcount.models.annotations import groundtruth
from inflection import camelize
from random import randint, choice
import glob
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import os
import re


def get(dataset):
    class_name = "{}Previewer".format(camelize(dataset))
    return globals()[class_name]()


class BasePreviewer():
    def show(self, index=None):
        path = self.get_path(index)
        print("Displaying {}".format(path))
        with self._create_plot(path) as plt:
            plt.show()

    def save(self, index):
        os.makedirs("tmp/previews/", exist_ok=True)
        path = self.get_path(index)
        dest = "tmp/previews/{}.jpg".format(index)
        print("Saving to {}".format(dest))
        with self._create_plot(path) as plt:
            png = "{}.png".format(dest[0:-4])
            plt.savefig(png)  # matlabplot only supports png, so convert.
            Image.open(png).save(dest, 'JPEG', quality=100)
            os.remove(png)

    def get_cmap(self):
        return None

    @contextmanager
    def _create_plot(self, path):
        img = mpimg.imread(path)
        fig = plt.figure()
        fig.suptitle('Ground Truth')

        ax1 = fig.add_subplot(121)
        ax1.imshow(img, cmap=self.get_cmap())
        anns = groundtruth.get(path)
        if anns.any():
            ax1.plot(anns[:, 0], anns[:, 1], 'r+')
            ax1.set_title("Annotations: {}".format(len(anns)))

        ax2 = fig.add_subplot(122)
        # Use diverging cmap: http://matplotlib.org/examples/color/colormaps_reference.html
        dm = density_map.generate(path, anns)
        ax2.imshow(dm, cmap='seismic')
        ax2.set_title("Density Map: {}".format(dm.sum()))

        yield plt
        plt.close()


class UcfPreviewer(BasePreviewer):
    def get_cmap(self):
        return "gray"

    def get_path(self, index=None):
        if not index:
            index = randint(1, 50)
        return "data/ucf/{}.jpg".format(index)


class MallPreviewer(BasePreviewer):
    def get_path(self, index=None):
        if not index:
            index = randint(1, 2000)
        return "data/mall/frames/seq_00{:04}.jpg".format(index)


class ShakecamPreviewer(BasePreviewer):
    def get_path(self, index=None):
        if not index:
            index = self.randindex()
        return "data/shakecam/shakeshack-{}.jpg".format(index)

    def randindex(self):
        path = choice(glob.glob('data/shakecam/shakeshack-*.jpg'))
        return int(re.match(r".*shakeshack-(\d+)\.", path).group(1))

    def index_from_path(self, path):
        return path[-14:-4]
