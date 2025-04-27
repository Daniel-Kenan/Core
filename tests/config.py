import sys
import os
import unittest
import pathlib
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json as json_lib 
from workflow_engine import execute_workflow
from workflow_engine_nodes import *

current_dir = pathlib.Path(__file__).parent.resolve()
workflow_dir = current_dir / "workflows"

def load_workflow(*args):
    print(args)
    if not args:
       for file in workflow_dir.iterdir():   
            simulate_workflow_exec(file.name)
    else : 
        for file in args:
            simulate_workflow_exec(file)

def simulate_workflow_exec(file):
    """
    ╔═══════════════════════════════════════════════════════════════════════╗
          Simulating workflow execution for :{file}
    ╚═══════════════════════════════════════════════════════════════════════╝
    Please note that the tests simulations were conducted manually to make sure that the workflow engine is working as expected.
    but later the tests will be automated to cover a large portion of the worflow engine.
    """

    print(f"""
    ╔═══════════════════════════════════════════════════════════════════════╗
          Simulating workflow execution for :{file}
    ╚═══════════════════════════════════════════════════════════════════════╝
    
""")  
    
    if file.endswith(".json"):
        with open(workflow_dir / file, "r") as file:
            json_string = file.read()
            
    workflow = json_lib.loads(json_string)
    print("Executing workflow test")
    result = execute_workflow(workflow)
    print(result, "\n\n")
