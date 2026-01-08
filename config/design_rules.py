import yaml
with open("config/config.yaml") as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)
design_rules = cfg.get('design_rules')

# min Distance from Bend
min_bend_angle = design_rules.get('Min Bend Angle', 30)

# Flange Area Dimensions
min_flange_length = design_rules.get('Min Flange Length', 10)
min_flange_width = design_rules.get('Min Flange Width', 30)

# Minimal Bending Angle
min_bend_angle = design_rules.get('Min Bend Angle', 35) #°