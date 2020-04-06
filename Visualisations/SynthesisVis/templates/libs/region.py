class Region():
    def __init__(self, area, sat):
        self.area = area
        self.sat = sat

    def __str__(self):
        return str(self.area) + " " + str(self.sat)

    def projection(self, param):
        return self.area[param]

    def check_other_dims(self, dims):
        for param in dims.keys():
            if not self.area[param][0] <= dims[param] <= self.area[param][1]:
                return False
        return True
