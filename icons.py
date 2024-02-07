BATTERY_BUTTON = [(5, 20), (18, 20), 0, (22, 20), (35, 20), 0, (18, 10), (18, 30), 0, (22, 15), (22, 25), 0]
SWITCH_BUTTON = [(5, 20), (13, 20), 0, (15, 20, 2), 10, (17, 18), (25, 14), 3, (25, 20), (35, 20)]

RESISTOR_BUTTON = [(5, 20), (10, 20), 0, (30, 20), (35, 20), 0, (10, 17), (10, 23), (30, 23), (30, 17), 1]
RESISTOR_F_BUTTON = [(5, 20), (10, 20), 0, (10, 17), (10, 23), (30, 23), (30, 17), 1,
                     (20, 10), (20, 14), (15, 14), (15, 17), (13, 15), 0, (15, 17), (17, 15), 0]
RESISTOR_C_BUTTON = [(5, 20), (10, 20), 0, (30, 20), (35, 20), 0, (10, 17), (10, 23), (30, 23), (30, 17), 1,
                     (12, 26), (28, 14), (25, 14), 3, (28, 14), (28, 16), 3]
VOLTAGE_METER_BUTTON = [(5, 20), (10, 20), 0, (30, 20), (35, 20), 0, (20, 20, 10), 10, (20, 20), 'V']
CURRENT_METER_BUTTON = [(5, 20), (10, 20), 0, (30, 20), (35, 20), 0, (20, 20, 10), 10, (20, 20), 'A']
ANY_METER_BUTTON = [(5, 20), (10, 20), 0, (30, 20), (35, 20), 0, (20, 20, 10), 10, (20, 20), 'A']

Battery_0 = {'w': 20, 'h': 30,
             'i': [(-5, 15), (7, 15), 0, (13, 15), (25, 15), 0, (7, 0), (7, 30), 0, (13, 8), (13, 22), 0, ]}
Switch_0 = {'w': 20, 'h': 16,
            'i': [(-5, 8), (0, 8), 0, (20, 8), (25, 8), 0, (3, 8, 2), 10, (4, 7), (18, 0), 3, ]}
Switch_1 = {'w': 20, 'h': 16,
            'i': [(-5, 8), (0, 8), 0, (20, 8), (25, 8), 0, (3, 8, 2), 10, (4, 7), (21, 6), 3, ]}
Resistor_0 = {'w': 40, 'h': 10,
              'i': [(-5, 5), (0, 5), 0, (40, 5), (45, 5), 0, (0, 0), (0, 10), (40, 10), (40, 0), 1, ]}
ResistorFlexible_0 = {'w': 40, 'h': 10,
                      'i': [(-5, 5), (0, 5), 0, (20, -10), (20, -5), 0, (0, 0), (0, 10), (40, 10), (40, 0), 1, ]}
ResistorChest_0 = {'w': 40, 'h': 10,
                   'i': [(-5, 5), (0, 5), 0, (40, 5), (45, 5), 0, (0, 0), (0, 10), (40, 10), (40, 0), 1, (5, 15),
                         (35, -5), (30, -5), 3, (35, -5), (34, 0), 0, ]}
Meter_0 = {'w': 20, 'h': 20,
           'i': [(-5, 10), (0, 10), 0, (20, 10), (25, 10), 0, (10, 10, 10), 10, ]}

ADD = [(4, 10), (16, 10), 0, (10, 4), (10, 16)]
MINUS = [(4, 10), (16, 10)]

ANALYSIS = [(27, 27), (30, 30), 0, (20, 20, 10), 10]
DELETE = [(10, 10), (30, 30), 0, (10, 30), (30, 10), 0]
HELP = [(20, 20, 12), 10, (20, 20), '?']
