# GIF Demo Configurations

This directory contains specialized YAML configurations optimized for creating demonstration GIFs.

## 📁 Available Configurations

### `west_lafayette_high_density.yaml`
- **Purpose**: High-activity demonstration with maximum visual impact
- **Features**: 30 vehicles, 1500 orders/hour, 6 charging stations
- **Best for**: Showcasing system capabilities and busy urban scenarios
- **GIF output**: High-energy, lots of movement and activity

### `west_lafayette_light_traffic.yaml`
- **Purpose**: Moderate activity level for clearer visualization
- **Features**: 15 vehicles, 800 orders/hour, 4 charging stations
- **Best for**: Educational purposes, easier to follow individual vehicles
- **GIF output**: Balanced activity, clear individual vehicle tracking

### `west_lafayette_charging_focus.yaml`
- **Purpose**: Emphasizes charging infrastructure usage
- **Features**: 25 vehicles, high battery consumption, 8 charging stations
- **Best for**: Demonstrating charging network efficiency and queue management
- **GIF output**: Frequent charging activities, station utilization patterns

## 🎬 How to Use

### Quick GIF Generation
```bash
# High density demo (recommended for README)
python tools/create_gif.py -c yaml_config/gif_demos/west_lafayette_high_density.yaml

# Light traffic demo 
python tools/create_gif.py -c yaml_config/gif_demos/west_lafayette_light_traffic.yaml

# Charging focus demo
python tools/create_gif.py -c yaml_config/gif_demos/west_lafayette_charging_focus.yaml
```

### Custom Parameters
```bash
# 15-second GIF with 80 frames
python tools/create_gif.py -c yaml_config/gif_demos/west_lafayette_high_density.yaml --duration 15 --max-frames 80

# Save individual frames for custom editing
python tools/create_gif.py -c yaml_config/gif_demos/west_lafayette_light_traffic.yaml --save-frames
```

## 🎯 Configuration Guidelines

When creating new GIF demo configurations:

### Optimization for GIFs
- **Duration**: Set to 60s minimum (system requirement), override with `--duration` parameter
- **time_step**: Use 0.05-0.1 for smooth animation
- **animation_fps**: 30 FPS works best for GIF conversion

### Visual Impact
- **High activity**: More vehicles and orders for impressive demos
- **Balanced view**: Fewer vehicles for educational clarity
- **Specific focus**: Emphasize particular features (charging, routing, etc.)

### Performance Considerations
- **Vehicle count**: 15-30 vehicles optimal for GIFs
- **Order rate**: 800-1500/hour provides good visual activity
- **Charging stations**: 4-8 stations show infrastructure usage

## 📊 Comparison Table

| Configuration | Vehicles | Orders/Hour | Stations | Best For |
|---------------|----------|-------------|----------|----------|
| High Density  | 30       | 1500        | 6        | Marketing, Impact |
| Light Traffic | 15       | 800         | 4        | Education, Clarity |
| Charging Focus| 25       | 1200        | 8        | Infrastructure Demo |

## 🚀 Adding New Configurations

To create a new GIF demo configuration:

1. Copy an existing configuration
2. Modify parameters for your use case
3. Update the name and comments
4. Test with: `python tools/create_gif.py -c your_config.yaml --duration 10`
5. Update this README with the new configuration

## 💡 Tips for Better GIFs

- **Higher activity** = more engaging but harder to follow
- **Lower activity** = clearer but potentially boring
- **Specialized scenarios** = great for demonstrating specific features
- **Always test** with short duration first (10-15 seconds) 