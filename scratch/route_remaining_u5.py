from grid_router import GridRouter
from test_autoroute import simplify_path

# True U5 pin positions on Row 2 (X = 110.24):
# Pin 35: (110.24, 90.0 + 12.70) = (110.24, 102.70) -> audio_in_from_daisy_plus -> R7 pin 1 (172.30, 97.90)
# Pin 37: (110.24, 90.0 + 7.62)  = (110.24, 97.62)  -> daisy_audio_in           -> C17 pin 1 (159.825, 91.60)
# Pin 39: (110.24, 90.0 + 2.54)  = (110.24, 92.54)  -> daisy_5v_power           -> C25 pin 1 (128.42, 136.51)

rem_router = GridRouter(x_min=90.0, x_max=180.0, y_min=70.0, y_max=155.0, step=0.5)

# Block other pins
# Route daisy_audio_in on layer 0 (F.Cu)
path_audio_in = rem_router.route_net((110.24, 97.62), (159.825, 91.60), layer=0, clearance=0.4)
if path_audio_in:
    s_audio_in = simplify_path(path_audio_in)
    print(f"SUCCESS: daisy_audio_in routed with {len(s_audio_in)} points")
else:
    print("FAILED daisy_audio_in")

# Route daisy_5v_power from (110.24, 92.54) to (128.42, 136.51) on layer 0 (F.Cu)
path_pwr = rem_router.route_net((110.24, 92.54), (128.42, 136.51), layer=0, clearance=0.6)
if path_pwr:
    s_pwr = simplify_path(path_pwr)
    print(f"SUCCESS: daisy_5v_power routed with {len(s_pwr)} points")
else:
    print("FAILED daisy_5v_power")

# Route audio_in_from_daisy_plus on layer 1 (B.Cu) from (110.24, 102.70) to (172.30, 97.90)
path_plus = rem_router.route_net((110.24, 102.70), (172.30, 97.90), layer=1, clearance=0.4)
if path_plus:
    s_plus = simplify_path(path_plus)
    print(f"SUCCESS: audio_in_from_daisy_plus routed with {len(s_plus)} points")
else:
    print("FAILED audio_in_from_daisy_plus")
