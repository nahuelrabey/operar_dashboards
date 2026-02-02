# Proposal: Interactive Graph with Horizontal Zoom (Plotly)

## Goal
Enable **Horizontal Zoom** and **Pan** on the performance graph. The user wants to inspect specific periods closely. The current chart (`st.line_chart`) is limited in interactivity, especially with the customized date axis used to remove gaps.

## Proposed Solution
Switch the visualization library from Streamlit's native `st.line_chart` (Altair-based) to **Plotly**.

### Why Plotly?
1.  **Native Zoom/Pan**: Supports box select, pan, and zoom x/y out of the box.
2.  **Gap Handling**: Has a dedicated feature (`rangebreaks`) to hide weekends and non-trading hours while keeping the axis as a true Datetime type (allowing proper time-based zooming).
3.  **Tooltips**: Superior hover information.

## Code Changes

### 1. Dependencies
- Install `plotly`.

### 2. `pages/01_CEDEARs_Analysis.py`
- Import `plotly.graph_objects as go`.
- Replace `st.line_chart(comparison_data)` with `st.plotly_chart(fig)`.
- **Refactor Plotting Logic**:
    - Create a Figure.
    - Add traces for GLD and each selected ticker.
    - Configure the Layout:
        - Enable `xaxis_rangeslider` (optional) or just simple zoom/pan tools.
        - **Gap Removal**:
            - For Daily data: configured `rangebreaks` to skip weekends (Sat, Sun).
            - For Intraday: skip non-trading hours (if complex) or stick to string-index hack if Plotly handles zoomed-in categorical axes better (it typically does).
            - **Preferred Approach**: Keep data as Datetime objects and use `rangebreaks` for a professional experience.

## Implementation Steps
1.  Add `plotly` to environment.
2.  Update dashboard code to generate a Plotly figure.
3.  Configure `rangebreaks` to remove weekends (Sat/Sun).
