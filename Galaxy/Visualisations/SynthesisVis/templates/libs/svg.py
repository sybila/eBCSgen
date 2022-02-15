import math
import colorsys
import numpy as np

# COLORS = {-2: '#cc5700', -1: 'red', 0: 'gray', 1: 'green', 2: '#1fb842'}
COLORS = {-2: 'gray', -1: 'red', 0: 'gray', 1: 'green', 2: 'gray'}

GRADIENT = \
'''
<defs>
    <linearGradient id='gradient'>
        <stop offset='0%'  stop-color='rgb(255, 0, 0)' />
        <stop offset='50%'  stop-color='rgb(255,255,0)' />
        <stop offset='100%' stop-color='rgb(0, 128, 0)' />
    </linearGradient>
</defs>
'''


class Picture():
    def __init__(self, bounds):
        self.regions = []
        self.width_bounds = {'min': 100, 'max': 600}
        self.width_bounds['len'] = self.width_bounds['max'] - self.width_bounds['min']
        self.height_bounds = {'min': 100, 'max': 600}
        self.height_bounds['len'] = self.height_bounds['max'] - self.height_bounds['min']
        self.header = "<svg width='{0}' height='{1}' xmlns='http://www.w3.org/2000/svg'>".format(
            self.width_bounds['max'] + 20, self.height_bounds['max'] + 100)
        self.footer = '</svg>'
        self.lines = []
        self.texts = []
        self.points = []
        self.regions = []
        self.bounds = bounds
        self.axis_description()

    def __str__(self):
        output = self.header
        for point in self.points:
            output += point + ' '
        for region in self.regions:
            output += region + ' '
        for line in self.lines:
            output += line + ' '
        for text in self.texts:
            output += text + ' '
        output += self.footer
        return output

    def axis_description(self):
        x_axis = np.linspace(self.bounds['x_min'], self.bounds['x_max'], 11)
        y_axis = np.linspace(self.bounds['y_min'], self.bounds['y_max'], 11)

        self.add_line(self.width_bounds['min'], self.width_bounds['min'],
                      self.width_bounds['max'], self.width_bounds['min'], 'black')
        self.add_line(self.height_bounds['min'], self.height_bounds['min'],
                      self.height_bounds['min'], self.height_bounds['max'], 'black')

        for i in range(11):
            y = self.height_bounds['min'] + (self.height_bounds['len'] / 10) * i
            self.add_line(self.width_bounds['min'], y, self.width_bounds['min'] - 20, y, 'black')
            self.add_text(5, y + 5, 0, '{0:.2f}'.format(y_axis[i]))

        for i in range(11):
            x = self.width_bounds['min'] + (self.width_bounds['len'] / 10) * i
            self.add_line(x, self.height_bounds['min'], x, self.height_bounds['min'] - 20, 'black')
            self.add_text(x - self.width_bounds['len'] / 10, 30, 45, '{0:.2f}'.format(x_axis[i]))

    def add_text(self, x, y, angle, text, size=25):
        self.texts.append("<text x='{0}' y='{1}' font-size='{2}' transform='rotate({3}, {0}, {1})'>{4}</text>" \
                          .format(x, y, size, angle, text))

    def add_line(self, x1, y1, x2, y2, color, width=5):
        self.lines.append("<line x1='{0}' y1='{1}' x2='{2}' y2='{3}' style='stroke:{5};stroke-width:{4}'/>" \
                          .format(x1, y1, x2, y2, width, color))

    def add_rectangle(self, x, y, w, h, color):
        self.regions.append("<rect x='{0}' y='{1}' width='{2}' height='{3}' fill='{4}' />" \
                            .format(x, y, w, h, color))

    def add_point(self, x, y, color):
        self.points.append("<circle cx='{0}' cy='{1}' r='{2}' stroke='{4}' stroke-width='{3}' fill='{4}' />" \
                           .format(x, y, 3, 3, color))

    def save(self, filename):
        f = open(filename, 'w')
        f.write(self.header)
        f.write(GRADIENT)
        for point in self.points:
            f.write(point + '\n')
        for region in self.regions:
            f.write(region + '\n')
        for line in self.lines:
            f.write(line + '\n')
        for text in self.texts:
            f.write(text + '\n')
        f.write(self.footer)
        f.close()

    def add_legend_reactangles(self):
        texts = ['TRUE', 'FALSE', 'UNKNOWN']
        colors = ['green', 'red', 'gray']

        y = self.height_bounds['max'] + 40

        for i in range(len(texts)):
            self.add_text(self.width_bounds['min'] + 70 + 150 * i, y + 20, 0, texts[i], 20)
        for i in range(len(colors)):
            self.add_rectangle(self.width_bounds['min'] + 35 + 150 * i, y, 25, 25, colors[i])

    def add_legend_points(self, min_v, max_v):
        x = self.width_bounds['min'] + 100
        y = self.height_bounds['max'] + 100
        self.add_rectangle(x, self.height_bounds['max'] + 30, 250, 25, 'url(#gradient)')
        self.add_line(x, self.height_bounds['max'] + 55, x + 250, self.height_bounds['max'] + 55, 'black', 3)

        values = [min_v, (min_v + max_v) / 2, max_v]

        for i in range(len(values)):
            self.add_line(x + i * 125, self.height_bounds['max'] + 55, x + i * 125, self.height_bounds['max'] + 65,
                          'black', 3)
            self.add_text(x - 30 + i * 125, y - 10, 0, '%.2f' % values[i])

    def load_rectangles(self, regions, x, y, dims):
        self.add_legend_reactangles()
        for region in regions:
            if region.check_other_dims(dims):
                norm_points = self.normalise_rectangle(region, x, y)
                x_pos = norm_points[0]
                y_pos = norm_points[2]
                width = (norm_points[1] - norm_points[0])
                height = (norm_points[3] - norm_points[2])
                self.add_rectangle(x_pos, y_pos, width, height, COLORS[region.sat])

    def normalise_rectangle(self, region, x, y):
        return [fit_to_picture(normalise(region.projection(x)[0], self.bounds['x_max'], self.bounds['x_min']),
                               self.width_bounds['len'], self.width_bounds['min']),
                fit_to_picture(normalise(region.projection(x)[1], self.bounds['x_max'], self.bounds['x_min']),
                               self.width_bounds['len'], self.width_bounds['min']),
                fit_to_picture(normalise(region.projection(y)[0], self.bounds['y_max'], self.bounds['y_min']),
                               self.height_bounds['len'], self.height_bounds['min']),
                fit_to_picture(normalise(region.projection(y)[1], self.bounds['y_max'], self.bounds['y_min']),
                               self.height_bounds['len'], self.height_bounds['min'])]

    def load_points(self, points, min_p, max_p, bounds, normalisation=True):
        self.add_legend_points(min_p, max_p)
        for (x, y, p) in points:
            x = fit_to_picture(normalise(x, bounds['w_max'], bounds['w_min']), self.width_bounds['len'],
                               self.width_bounds['min'])
            y = fit_to_picture(normalise(y, bounds['h_max'], bounds['h_min']), self.height_bounds['len'],
                               self.height_bounds['min'])
            if normalisation:
                p = normalise(p, max_p, min_p)
            self.add_point(x, y, colorify(p))


def normalise(value, min_value, max_value):
    return (max_value - value) / (max_value - min_value)


def fit_to_picture(value, multi, add):
    return value * multi + add


def colorify(value):
    if value < 0.5:
        return 'rgb(255,{0},0)'.format(int(255 * (1 - normalise(value, 0, 0.5))))
    return 'rgb({0},{1},0)'.format(int(255 * (normalise(value, 0.5, 1))), 128 + int(128 * (normalise(value, 0.5, 1))))
