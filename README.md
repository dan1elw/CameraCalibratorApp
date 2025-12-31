Camera Calibrator App
=====================

Project that helps calibrate a camera using calibration images, visualize detected corners, and export camera intrinsics and distortion parameters.

Quick overview
--------------
- Purpose: assist with camera intrinsic and distortion calibration using standard chessboard patterns, plus provide simple visualization and a console-based workflow.
- Language: Python
- Run: `python main.py`

Module layout
-------------
The code lives in the `camera_calibrator` package. Key modules:

- `camera_calibrator/cal.py`: Core calibration routines. Detects chessboard corners across image pairs or sets, calculates intrinsic matrix, distortion coefficients, reprojection error, and exports results.
- `camera_calibrator/camera.py`: Representation of a calibrated camera and helpers for applying and removing distortion, saving/loading calibration parameters.
- `camera_calibrator/image.py`: Image loading, preprocessing, and utilities for converting and handling image sets used for calibration.
- `camera_calibrator/graphics.py`: Visualization helpers — drawing detected corners, reprojection points, and overlaying results for inspection.
- `camera_calibrator/console.py`: Simple CLI/console interface for running calibration workflows, stepping through image sets, and saving results.
- `camera_calibrator/__init__.py`: Package exports and version metadata.

Example data
------------
Example chessboard image sets are included under the `example/` directory:

- `example/example_left_30mm/`
- `example/example_right_30mm/`

These are sample image folders for testing the calibration pipeline.

Features
--------
- Detect chessboard corners in image sets (single or stereo image pairs).
- Compute camera intrinsics (focal length, principal point) and distortion coefficients.
- Provide reprojection error metrics to assess calibration quality.
- Visualize detected corners and reprojections to validate results.
- Save and load calibration parameters for later use.

Installation
------------
1. Create a Python virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

Usage
-----
- Run the main application:

```bash
python main.py
```

- Use the console interface (if available) to point at image directories, run detection, compute calibration, and save results. Refer to `camera_calibrator/console.py` for available commands and options.

Development notes
-----------------
- The calibration routines assume chessboard-style calibration images. Adjust detection settings in `camera_calibrator/cal.py` if you use an alternate pattern.
- Visualization helpers in `camera_calibrator/graphics.py` are lightweight — they draw overlays for inspection but are not a full GUI.

Files to inspect
----------------
- See [camera_calibrator/cal.py](camera_calibrator/cal.py) for calibration algorithms.
- See [camera_calibrator/camera.py](camera_calibrator/camera.py) for the camera parameter model.
- See [camera_calibrator/console.py](camera_calibrator/console.py) for the CLI workflows.

Contributing
------------
- Feel free to open issues or submit pull requests. Keep changes focused and include tests for algorithmic changes where possible.

Contact
-------
If you need help or want new features, open an issue or contact the repository owner.
