def transform(self, x, y):
    return self.transform_perspective(x, y)
    # return self.transform_2d(x, y)


def transform_2d(self, x, y):
    return int(x), int(y)


def transform_perspective(self, x, y):
    lin_y = y * self.taskas_y / self.height
    if lin_y > self.taskas_y:
        lin_y = self.taskas_y
    diff_x = x - self.taskas_x
    diff_y = self.taskas_y - lin_y
    factor_y = diff_y / self.taskas_y
    factor_y = pow(factor_y, 4)
    tr_x = self.taskas_x + diff_x * factor_y
    tr_y = self.taskas_y - factor_y * self.taskas_y
    return int(tr_x), int(tr_y)
