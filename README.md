# gm/Id Visualization Tool

This tool provides an interactive web interface for exploring the **gm/Id methodology**. It runs standard DC sweeps and visualizes key relationships to aid in analog circuit design.

## Prerequisites

*   **ngspice**: Must be installed and accessible in your path.
*   **IHP PDK**: The `ihp-sg13g2` PDK must be installed.
    *   The tool expects `PDK_ROOT` and `PDK` environment variables to be set.

## Installation

This project uses `uv` for dependency management.

1.  **Clone the repository**.
2.  **Install dependencies**:
    ```bash
    uv sync
    ```

## Usage

Run the Streamlit application:

```bash
uv run streamlit run app.py
```

Navigate to the local URL provided (usually `http://localhost:8501`).

1.  Select your **Device Type** from the sidebar.
2.  Adjust **Dimensions** (Width, Length, Multipliers).
3.  Set **Bias Conditions** ($V_{DS}$, $V_{BS}$).
4.  Configure the **Sweep Range** ($V_{GS}$ Max).
5.  Click **Run Simulation**.

## Project Structure

*   `app.py`: Main Streamlit application entry point.
*   `simulation/`: Core simulation logic.
    *   `runner.py`: Orchestrates ngspice execution.
    *   `templates.py`: SPICE netlist templates.
    *   `parser.py`: Extracts and processes simulation data.
*   `plotting/`: Chart generation logic `charts.py` using Plotly.
