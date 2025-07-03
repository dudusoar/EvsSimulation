# GIF Creation Guide

This guide explains how to create demonstration GIFs for the EV Simulation project.

## 🎬 Quick Start

### Recommended Method
```bash
# Activate virtual environment
.venv\Scripts\activate

# Create high-impact demo GIF (default)
python tools/create_gif.py

# Alternative configurations
python tools/create_gif.py -c yaml_config/gif_demos/west_lafayette_light_traffic.yaml
python tools/create_gif.py -c yaml_config/gif_demos/west_lafayette_charging_focus.yaml
```

## 📁 Available Configurations

See `yaml_config/gif_demos/README.md` for detailed configuration options:

- **High Density**: Maximum visual impact with 30 vehicles
- **Light Traffic**: Educational clarity with 15 vehicles  
- **Charging Focus**: Infrastructure demonstration with frequent charging

## 🛠️ Advanced Usage

### Custom Parameters
```bash
# Short 10-second GIF with 60 frames
python tools/create_gif.py --duration 10 --max-frames 60

# Save individual frames for custom editing
python tools/create_gif.py --save-frames --frames-dir custom_frames/

# Different output location
python tools/create_gif.py -o marketing/demo.gif
```

### Frame Management

The GIF recorder automatically manages memory:

- **Default**: Frames stored in memory → Generate GIF → Auto cleanup
- **With --save-frames**: Frames saved to disk + memory → Generate GIF → Memory cleanup

#### Memory Usage
- **Per frame**: ~500KB (800x600 PNG)
- **80 frames**: ~40MB RAM
- **After GIF**: 0MB (auto cleanup)

## 🎯 GIF Specifications

### Output Properties
- **Size**: 600-800KB typical
- **Duration**: 10-15 seconds recommended
- **Dimensions**: ~800x600px
- **Frame rate**: ~10 FPS
- **Format**: Optimized GIF with loop

### Content Showcase
- 🚗 Vehicle fleet movement on real map
- 📍 Order pickup/dropoff locations
- ⚡ Charging station usage patterns
- 🔋 Real-time battery status
- 📊 Dynamic statistics overlay

## 🔧 Customization

### Creating New Demo Configurations

1. Copy existing config from `yaml_config/gif_demos/`
2. Modify parameters:
   - `vehicles.count`: 15-30 optimal for GIFs
   - `orders.generation_rate`: 800-1500/hour for activity
   - `charging_stations.count`: 4-8 for infrastructure demo
3. Test with short duration: `--duration 10`

### Visual Impact Tips

- **More vehicles** = impressive but harder to follow
- **Fewer vehicles** = clearer individual tracking
- **Higher speeds** = more dynamic movement
- **Lower charging threshold** = more charging activity

## 🚨 Troubleshooting

### Common Issues

**Q: GIF file too large?**
```
Solutions:
- Reduce --max-frames (fewer frames)
- Increase --frame-interval (capture less frequently)
- Use lighter traffic configuration
```

**Q: Simulation crashes during recording?**
```
Solutions:
- Check virtual environment activation
- Verify YAML configuration syntax
- Try shorter --duration first
```

**Q: Poor animation quality?**
```
Solutions:
- Ensure window is properly sized before recording
- Use configurations with balanced vehicle counts
- Test different gif_frame_duration settings
```

## 📊 Performance Guidelines

### Recommended Settings by Use Case

| Use Case | Vehicles | Duration | Frames | Configuration |
|----------|----------|----------|--------|---------------|
| README Demo | 30 | 15s | 80 | high_density |
| Education | 15 | 20s | 100 | light_traffic |
| Infrastructure | 25 | 15s | 80 | charging_focus |
| Custom | 20-30 | 10-20s | 60-100 | modified |

## 🎥 Alternative Methods

### Screen Recording (Backup)

If the automated tool doesn't work:

1. **Run simulation**:
   ```bash
   python main.py -c yaml_config/gif_demos/west_lafayette_high_density.yaml
   ```

2. **Record screen**: Windows Game Bar (Win+G) or OBS Studio

3. **Convert to GIF**:
   ```bash
   ffmpeg -i recording.mp4 -vf "fps=10,scale=800:-1" demo.gif
   ```

## 📁 Output Files

```
assets/
├── demo-python-simulation.gif    # Main demo GIF (committed)
└── frames/ (if --save-frames)     # Individual frames (gitignored)
    ├── frame_0000.png
    ├── frame_0001.png
    └── ...
```

The generated GIF is automatically referenced in `README.md` and displays on GitHub! 