import sys
import os
import unittest
import pathlib
import json

# Ensure project root is on path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from workflow_engine import execute_workflow

class WorkflowEngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Directory containing JSON workflow definitions
        cls.workflow_dir = pathlib.Path(__file__).parent.resolve() / 'workflows'
        if not cls.workflow_dir.exists():
            raise FileNotFoundError(f"Workflows directory not found: {cls.workflow_dir}")

    def test_all_workflows_execute_successfully(self):
        """
        Iterate over all .json files and ensure each workflow runs without error,
        producing a context dict with success=True for each node.
        """
        for wf_file in sorted(self.workflow_dir.glob('*.json')):
            with self.subTest(workflow=wf_file.name):
                with wf_file.open() as f:
                    workflow = json.load(f)
                # Execute workflow
                result = execute_workflow(workflow)
                # Must return a dict
                self.assertIsInstance(result, dict)
                # Every node ID should be present in result with success True
                node_ids = [node['id'] for node in workflow.get('nodes', [])]
                for nid in node_ids:
                    self.assertIn(nid, result, f"Missing result for node {nid}")
                    res = result[nid]
                    self.assertIsInstance(res, dict)
                    self.assertIn('success', res)
                    self.assertTrue(res['success'], f"Node {nid} failed execution")

    def test_c_code_workflow_outputs(self):
        """
        Specific assertions for the c_code.json workflow to verify code execution ordering.
        """
        wf_file = self.workflow_dir / 'c_code.json'
        self.assertTrue(wf_file.exists(), "c_code.json not found in workflows directory")
        with wf_file.open() as f:
            workflow = json.load(f)
        result = execute_workflow(workflow)

        # Verify Python node ran
        self.assertIn('2', result)
        self.assertTrue(result['2']['output'].startswith('Executed Python'), "Python node did not run correctly")
        # Verify C node ran
        self.assertIn('1', result)
        self.assertTrue(result['1']['output'].startswith('Executed C'), "C node did not run correctly")
        # Verify JavaScript node ran
        self.assertIn('4', result)
        self.assertTrue(result['4']['output'].startswith('Executed JavaScript'), "JS node did not run correctly")

if __name__ == '__main__':
    unittest.main()
