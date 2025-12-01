import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add sibling directories to path
current_dir = os.path.dirname(os.path.abspath(__file__))
workspace_dir = os.path.dirname(current_dir)
sys.path.append(os.path.join(workspace_dir, 'environment_state_modul'))
# sys.path.append(os.path.join(workspace_dir, 'user_state_module'))

# Try importing environment module components
try:
    from environment_dynamics import DEFAULT_ENVIRONMENT_VARIABLES
    from arbitration_layer import ResourceArbitrator, UserResource, TaskRequest
    ENV_MODULE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import environment_state_modul: {e}")
    ENV_MODULE_AVAILABLE = False

class AgentManager:
    def __init__(self):
        self.agents = []
        self.agent_list_path = os.path.join(current_dir, 'agent_list.txt')
        self.load_agents()

    def load_agents(self):
        """Loads agents from agent_list.txt"""
        if not os.path.exists(self.agent_list_path):
            print("agent_list.txt not found.")
            return

        with open(self.agent_list_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 2:
                    self.agents.append({
                        'date': parts[0],
                        'module': parts[1],
                        'type': parts[2] if len(parts) > 2 else 'Unknown'
                    })
        
        print(f"Loaded {len(self.agents)} agents.")

    def run_environment_check(self, time_available: float = 60, energy_available: float = 80):
        """
        Runs the environment state check and arbitration.
        """
        if not ENV_MODULE_AVAILABLE:
            print("Environment module not available.")
            return

        print("\n--- Starting Environment Check ---")
        
        # Initialize Arbitrator with default variables
        # In a real scenario, these might be loaded from a database or persistent state
        arbitrator = ResourceArbitrator(DEFAULT_ENVIRONMENT_VARIABLES)
        
        # Generate requests
        requests = arbitrator.generate_requests(time_horizon=1.0)
        
        print(f"Generated {len(requests)} task requests from environment agents.")
        
        # Define User Resources (Context)
        user_resources = UserResource(
            time_available=time_available,
            energy_available=energy_available
        )
        print(f"User Resources: Time={user_resources.time_available}, Energy={user_resources.energy_available}")
        
        # Arbitrate
        accepted, rejected = arbitrator.arbitrate(user_resources, requests)
        
        print(f"\nAccepted Tasks ({len(accepted)}):")
        for task in accepted:
            print(f" - {task.variable_name}: Cost(T={task.required_time:.1f}, E={task.required_energy:.1f}), Loss prevented={task.marginal_utility:.2f}")
            
        print(f"\nRejected Tasks ({len(rejected)}):")
        for task in rejected:
            print(f" - {task.variable_name}: Future Loss={task.future_penalty_if_ignored:.2f}")
            
        return accepted, rejected

if __name__ == "__main__":
    manager = AgentManager()
    manager.run_environment_check()

