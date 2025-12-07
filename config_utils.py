import json
import os

def load_global_config():
    """Load global configuration from config/global.json"""
    try:
        with open("config/global.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def resolve_config_path(config_path):
    """Resolve file path relative to project root"""
    if not os.path.isabs(config_path):
        return os.path.abspath(config_path)
    return config_path

def load_process_config():
    """
    Load the default or first available process configuration.
    Returns:
        tuple: (config_dict, process_name) or (None, error_message)
    """
    # Load global settings first
    global_config = load_global_config()
    
    # Determine which process to load
    # For now, we take the first available process in the registry
    processes = global_config.get("processes", {})
    if not processes:
        return None, "No processes defined in global configuration."
        
    # Default to first one
    process_name = list(processes.keys())[0]
    config_file = processes[process_name]
    
    full_config_path = resolve_config_path(config_file)
    
    try:
        with open(full_config_path, "r") as f:
             process_config = json.load(f)
             # Merge process config into global
             # Global acts as base, Process specific overrides/extends
             final_config = global_config.copy()
             final_config.update(process_config)
             return final_config, None
             
    except FileNotFoundError:
        return None, f"Configuration file for {process_name} not found at {full_config_path}."
