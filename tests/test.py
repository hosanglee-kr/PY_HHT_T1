
import sys
import os
import pytest

# Add the src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from Py_HHT_T2_001 import main


#from src.a import main
#from src.Py_HHT_T2_001 import main

def test_main(capsys):
    # Run the main function
    main()
    
    # Capture the output of the main function
    captured = capsys.readouterr()
    
    # Print the captured output for debugging purposes
    print("Captured Output:")
    print(captured.out)

    print("test.py Current working directory:", os.getcwd())

    
