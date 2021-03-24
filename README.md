# wsnsim: Wireless Sensor Network Simulator
This is another Wireless Sensor Network simulator, this time in Python3.

Currently, two routing protocols are implemented: min-hop, ETX (mean delay) and Deadline Achievement Probability (DAP).

## Setup

1. Clone the repository: 
    
    `git clone https://github.com/mesepulveda/wsnsim.git`
    
2. Change to the repository folder:
    
    `cd wsnsim`
    
3. Create a virtual enviroment:
    
    `python3 -m venv venv`
    
4. Activate the virtual enviroment:
    
    `source venv/bin/activate`
    
5. Install the requirements:
    
    `pip3 install -r requirements.txt`
    
6. Append the project’s root directory to PYTHONPATH:
    
    `export PYTHONPATH="${PYTHONPATH}:${PWD}"`

## Run examples
- `python3 tests/simple_test.py`
- `python3 tests/complex_test.py`
- `python3 tests/pdf_test.py`
- `python3 tests/paper_example.py`

## Development
- Read the code.
- Read about `SimPy` and other dependencies.
- If you still have questions, write to Matías Sepúlveda (mesepulveda@uc.cl).
