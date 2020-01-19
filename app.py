import flask
from flask import request, jsonify
import scipy.interpolate
import numpy as np

app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return '''<h1>This is the main testing page</h1>
<p>A prototype API for distant reading of science fiction novels.</p>'''

sensor_1 = []
@app.route('/sensor1')
def sensor_1():
    global sensor_1

    date = request.args.get('date')
    time = request.args.get('time')
    xloc = int(request.args.get('xloc'))
    yloc = int(request.args.get('yloc'))
    temp = float(request.args.get('temp'))
    humidity = float(request.args.get('humidity'))

    sensor_1 = [date, time, xloc, yloc, temp, humidity]
    return '''<h1> The new value for sensor 1: {}</h1>'''.format(sensor_1)

sensor_2 = []
@app.route('/sensor2')
def sensor_2():
    global sensor_2

    date = request.args.get('date')
    time = request.args.get('time')
    xloc = int(request.args.get('xloc'))
    yloc = int(request.args.get('yloc'))
    temp = float(request.args.get('temp'))
    humidity = float(request.args.get('humidity'))

    sensor_2 = [date, time, xloc, yloc, temp, humidity]
    return '''<h1> The new value for sensor 2: {}</h1>'''.format(sensor_2)




def construct_dict_to_return(sensor1, sensor2):
    # sensor1 = [date, time, xloc, yloc, temp, humidity]
    def sens_to_prob(temp, humidity):
        a = 1
        b = 1
        c = 1.5
        inter = np.exp(-0.25 * (a - b * humidity + c * temp))
        probability = 1 / (1 + inter)
        return probability

    sens1 = [sensor1[2], sensor1[3], sens_to_prob(sensor1[4], sensor1[5])]
    sens2 = [sensor2[2], sensor2[3], sens_to_prob(sensor2[4], sensor2[5])]

    def interpolation(sensor_probs, k=10):
        def add_in_corners(list):
            corner_points_probs = [[-200, -200, 0], [-200, 200, 0], [200, -200, 0], [200, 200, 0]]
            return list + corner_points_probs

        # input: a list from each sensor of lists of x,y,prob
        sensor_probs_w_corners = np.array(add_in_corners(sensor_probs))
        assert sensor_probs_w_corners.shape[1] == 3
        point_cords = sensor_probs_w_corners[:, 0:2]
        probs_at_points = sensor_probs_w_corners[:, 2]

        print(point_cords)
        print(probs_at_points)
        spline_land = scipy.interpolate.CloughTocher2DInterpolator(point_cords, probs_at_points)

        xrange_min, xrange_max = (0, 100)
        yrange_min, yrange_max = (0, 100)
        grid_x, grid_y = np.mgrid[xrange_min:xrange_max:k, yrange_min:yrange_max:k]

        grid_probs = spline_land(grid_x, grid_y)

        return grid_probs

    grid = interpolation([sens1, sens2])

    data_dicts = []
    for x_cord in range(grid.shape[0]):
        for y_cord in range(grid.shape[1]):
            data_dicts.append({'long' : x_cord, 'lat' : y_cord, 'mag' : grid[x_cord, y_cord]})

    return data_dicts


@app.route('/summary')
def summary():
    data_dict = construct_dict_to_return(sensor_1, sensor_2)
    return jsonify(data_dict)

app.run()