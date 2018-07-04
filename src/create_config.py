
import yaml
import os

def create_config():
    config = {
        "output": {  # Sets the output folder and gets previous optimization
            "saving_dir": "/path/to/folder",
            "previous": [None],
            "folder": "TEST"
        },
        "params": {  # If True params are active
            "Dwelltime": False,
            "Exc/Power": False,
            "STED/Power": False,
            "Line_Step": False,
            "Rescue/Signal_Level": False,
            "Rescue/Strength": False
        },
        "objectives": {  # If True objectives are active
            "Signal_SQRT": False,
            "Signal_Ratio": False,
            "Autocorrelation": False,
            "FWHM": False,
            "Bleach": False,
            "Quality": False,
            "Quality_Last": False,
            "TotalTime": False,
            "FRC": False
        },
        "params_space": {  # Sets the min, max and number of points for the parameter space
            "Dwelltime": [10e-6, 100e-6, 12],
            "Exc/Power": [0.01, 0.4, 12],
            "STED/Power": [0.1, 0.6, 10],
            "Line_Step": [10, 25, 2],
            "Rescue/Signal_Level": [5, 105, 10],
            "Rescue/Strength": [0.1, 10, 20]
        },
        "params_set": { # Sets the laser_id, step_id and channel_id
            "Exc/Power": 4,
            "STED/Power": 5,
            "Line_Step": 0,
            "Rescue/Signal_Level": 0,
            "Rescue/Strength": 0
        },
        "objectives_values": {  # Sets the value of the different objectives
            "Signal_SQRT": 75,
            "Signal_Ratio": 75,
            "FRC": 20e-3
        },
        "noise_ub_objectives": {  # Sets the values of the upper bound limits on the noise
            "Signal_SQRT": 2,
            "Signal_Ratio": 2,
            "Autocorrelation": 0.3,
            "FWHM": 5,
            "Bleach": 0.1,
            "Quality": 0.1,
            "Quality_Last": 0.1,
            "FRC": 0.1
        },
        "autoquality": { # sets the parameters of QualityNet
            "IP": "172.16.13.216",
            "port": 5000
        },
        "autopref": { # sets the parameters of PrefNet
            "IP": "qualinet.duckdns.org",
            "port": 5002
        },
        "with_time" : False, # consider imaging time as an objective when making decisions
        "pseudo_points": False # hallucinate points in the regression model (e.g. to counter border effect)
    }
    return config

# with open(os.path.join(os.getcwd(), "config"), "w") as f:
#     yaml.dump(create_config(), f)
