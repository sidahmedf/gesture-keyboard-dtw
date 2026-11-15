import math

def interpolate(a:(float, float), b:(float, float), d:float) -> (float, float):

    total_distance = math.dist(a, b)

    if total_distance == 0:
        return a
    t = d / total_distance

    x1, y1 = a
    x2, y2 = b

    interp_x = x1 + (x2 - x1) * t
    interp_y = y1 + (y2 - y1) * t

    return (interp_x, interp_y)

def resample(stroke: list[(float,float)], d:float) -> list[(float,float)]:
    if len(stroke) < 2:
        return stroke

    result = [stroke[0]]
    current = stroke[0]

    for i in range(len(stroke) - 1):
        p1 = stroke[i]
        p2 = stroke[i + 1]

        while math.dist(current, p2) >= d:
            p3 = interpolate(current, p2, d)
            result.append(p3)
            current = p3

    result.append(stroke[-1])
    return result