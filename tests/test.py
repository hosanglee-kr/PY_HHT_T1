import pytest
#from src.a import main
from src.Py_HHT_T2_001 import main

def test_main(capsys):
    # Run the main function
    main()
    
    # Capture the output of the main function
    captured = capsys.readouterr()
    
    # Print the captured output for debugging purposes
    print("Captured Output:")
    print(captured.out)
    
