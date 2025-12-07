import pytest
import sys
import os

# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.runner import run_dc_sweep
import config_utils

@pytest.fixture
def config():
    conf, _ = config_utils.load_process_config()
    return conf

def test_nmos_sweep(config):
    """Test standard NMOS DC sweep."""
    if not config:
        pytest.skip("No configuration loaded")

    df = run_dc_sweep(
        device_name="sg13_lv_nmos",
        width=10e-6,
        length=1e-6,
        vds=0.9,
        vgs_max=1.8,
        ng=1,
        m=1,
        sim_config=config
    )
    
    assert df is not None, "Simulation returned None"
    assert not df.empty, "DataFrame is empty"
    assert 'gm_id' in df.columns, "Derived column 'gm_id' missing"
    assert 'id' in df.columns

def test_pmos_sweep(config):
    """Test standard PMOS DC sweep."""
    if not config:
        pytest.skip("No configuration loaded")
        
    df = run_dc_sweep(
        device_name="sg13_lv_pmos",
        width=10e-6,
        length=1e-6,
        vds=0.9,
        vgs_max=1.8,
        ng=1,
        m=1,
        sim_config=config
    )
    assert df is not None
    assert not df.empty

def test_hv_nmos_sweep(config):
    """Test High-Voltage NMOS Sweep."""
    if not config:
        pytest.skip("No configuration loaded")

    df = run_dc_sweep(
        device_name="sg13_hv_nmos",
        width=10e-6,
        length=1e-6,
        vds=3.3,
        vgs_max=3.3,
        ng=1,
        m=1,
        sim_config=config
    )
    assert df is not None
    assert not df.empty

def test_hv_pmos_sweep(config):
    """Test High-Voltage PMOS Sweep."""
    if not config:
        pytest.skip("No configuration loaded")

    df = run_dc_sweep(
        device_name="sg13_hv_pmos",
        width=10e-6,
        length=1e-6,
        vds=3.3,
        vgs_max=3.3,
        ng=1,
        m=1,
        sim_config=config
    )
    assert df is not None
    assert not df.empty
