# Tools Directory

This directory contains utility scripts and tools for the EV Simulation project.

## 📁 Available Tools

### `create_gif.py` - GIF Generation Tool

Create demonstration GIFs from simulation runs for marketing and documentation purposes.

#### Quick Usage
```bash
# Default high-density demo
python tools/create_gif.py

# Light traffic demo
python tools/create_gif.py -c yaml_config/gif_demos/west_lafayette_light_traffic.yaml

# Charging infrastructure demo
python tools/create_gif.py -c yaml_config/gif_demos/west_lafayette_charging_focus.yaml
```

#### Advanced Options
```bash
# Custom duration and frame count
python tools/create_gif.py --duration 20 --max-frames 100

# Save individual frames for editing
python tools/create_gif.py --save-frames --frames-dir my_frames/

# Different output location
python tools/create_gif.py -o marketing/demo.gif
```

#### Features
- ✅ Multiple preset configurations in `yaml_config/gif_demos/`
- ✅ Customizable frame count and duration
- ✅ Optional individual frame export
- ✅ Automatic memory cleanup
- ✅ Progress tracking during generation

## 🚀 Adding New Tools

When adding new utility scripts to this directory:

1. **Create descriptive names**: Use clear, action-oriented names
2. **Add documentation**: Include usage examples and parameter descriptions
3. **Update this README**: Add your tool to the list above
4. **Use project structure**: Import from project root using `sys.path.append()`

### Template for New Tools

```python
#!/usr/bin/env python3
"""
Tool Name - Brief Description
Detailed description of what this tool does
"""

import sys
from pathlib import Path

# Add project path
sys.path.append(str(Path(__file__).parent.parent))

def main():
    # Tool implementation
    pass

if __name__ == "__main__":
    main()
```

## 📋 Tool Guidelines

- **Standalone operation**: Each tool should work independently
- **Clear output**: Provide informative progress and result messages
- **Error handling**: Handle exceptions gracefully with helpful error messages
- **Command line interface**: Use argparse for configurable parameters
- **Documentation**: Include help text and usage examples 