#!/usr/bin/env python3
import sys
sys.path.append('tools')

from units_utils import *

# Test 1: Flächenoptimierung
print("=== Test 1: Flächenoptimierung ===")
area_m2 = 0.0019635 * ureg.meter**2
print(f"Ursprung: {area_m2}")
print(f"Dimensionalität: {area_m2.dimensionality}")
print(f"Meter²-Dimensionalität: {(ureg.meter ** 2).dimensionality}")
print(f"Gleich? {area_m2.dimensionality == (ureg.meter ** 2).dimensionality}")

optimized = optimize_output_unit(area_m2, "mm")
print(f"Optimiert: {optimized}")

# Test 2: Direkte Flächenoptimierung
print("\n=== Test 2: Direkte Flächenoptimierung ===")
area_opt = optimize_area_unit(area_m2, "mm")
print(f"Flächen-optimiert: {area_opt}")

# Test 3: Verschiedene Flächengrößen
print("\n=== Test 3: Verschiedene Flächengrößen ===")
areas = [
    1e-8,   # 0.01 mm²
    1e-6,   # 1 mm²
    1e-4,   # 1 cm²
    0.01,   # 1 dm²
    1,      # 1 m²
    1e6     # 1 km²
]

for area_val in areas:
    q = area_val * ureg.meter**2
    opt = optimize_area_unit(q, "mm")
    print(f"{area_val} m² -> {opt}") 