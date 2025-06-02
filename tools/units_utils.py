#!/usr/bin/env python3
"""
Units Utility für Engineering MCP Server

Dieses Modul behandelt alle Einheiten-Operationen:
- Eingabe-Validierung (Einheiten müssen vorhanden sein)
- Umrechnung in SI-Einheiten
- Größenordnungs-optimierte Ausgabe in gleicher Grundeinheit
"""

import pint
from typing import Dict, Any, Union, Tuple
import re

# Pint Unit Registry
ureg = pint.UnitRegistry()

class UnitsError(Exception):
    """Fehler bei Einheiten-Operationen"""
    pass

def parse_value_with_unit(value_str: str) -> Tuple[float, str]:
    """
    Parst einen String mit Wert und Einheit.
    
    Args:
        value_str: String wie "5.2 mm" oder "100 bar"
        
    Returns:
        Tuple: (wert, einheit_string)
        
    Raises:
        UnitsError: Wenn keine Einheit erkannt wird
    """
    if not isinstance(value_str, str):
        raise UnitsError(f"Eingabe muss String mit Einheit sein, erhalten: {type(value_str)}")
    
    # Regex für Zahl + Einheit
    pattern = r'^\s*([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)\s*([a-zA-Z°]+.*?)\s*$'
    match = re.match(pattern, value_str.strip())
    
    if not match:
        raise UnitsError(f"Keine gültige Einheit in '{value_str}' gefunden. Format: 'Wert Einheit' (z.B. '5.2 mm')")
    
    value = float(match.group(1))
    unit_str = match.group(2).strip()
    
    return value, unit_str

def convert_to_si(value_str: str) -> pint.Quantity:
    """
    Konvertiert Eingabe-String in SI-Einheiten.
    
    Args:
        value_str: String wie "5.2 mm"
        
    Returns:
        pint.Quantity in SI-Einheiten
        
    Raises:
        UnitsError: Bei Parsing- oder Konvertierungsfehlern
    """
    try:
        value, unit_str = parse_value_with_unit(value_str)
        
        # Pint Quantity erstellen
        quantity = value * ureg(unit_str)
        
        # In SI umwandeln
        si_quantity = quantity.to_base_units()
        
        return si_quantity
        
    except Exception as e:
        if isinstance(e, UnitsError):
            raise
        raise UnitsError(f"Fehler beim Konvertieren von '{value_str}': {str(e)}")

def optimize_output_unit(si_quantity: pint.Quantity, reference_unit_str: str) -> pint.Quantity:
    """
    Optimiert die Ausgabeeinheit basierend auf Größenordnung.
    Behält die gleiche Grundeinheit wie die Referenz-Eingabe.
    
    Args:
        si_quantity: Ergebnis in SI-Einheiten
        reference_unit_str: Original-Einheit der Eingabe (z.B. "mm")
        
    Returns:
        pint.Quantity mit optimierter Einheit
    """
    try:
        # Bestimme Dimensionalität basierend auf der Ergebnis-Quantity
        result_dimensionality = si_quantity.dimensionality
        magnitude = si_quantity.magnitude
        
        # Spezialbehandlung für verschiedene Dimensionalitäten
        if result_dimensionality == (ureg.meter ** 2).dimensionality:
            # Flächeneinheiten
            return optimize_area_unit(si_quantity, reference_unit_str)
        elif result_dimensionality == (ureg.meter ** 3).dimensionality:
            # Volumeneinheiten - später implementieren
            return si_quantity
        elif result_dimensionality == ureg.pascal.dimensionality:
            # Druckeinheiten
            return optimize_pressure_unit(si_quantity, reference_unit_str)
        elif result_dimensionality == ureg.meter.dimensionality:
            # Längeneinheiten
            return optimize_length_unit(si_quantity, reference_unit_str)
        else:
            # Fallback: nutze SI-Einheit
            return si_quantity
            
    except Exception:
        # Fallback: SI-Einheit zurückgeben
        return si_quantity

def optimize_length_unit(si_quantity: pint.Quantity, reference_unit_str: str) -> pint.Quantity:
    """
    Optimiert Längeneinheiten basierend auf Größenordnung.
    """
    try:
        magnitude = si_quantity.magnitude  # in Metern
        
        # Häufige Einheiten-Präfixe (von klein zu groß)
        prefixes = [
            ('n', 1e-9), ('μ', 1e-6), ('m', 1e-3), ('c', 1e-2), 
            ('', 1), ('da', 1e1), ('h', 1e2), ('k', 1e3), 
            ('M', 1e6), ('G', 1e9), ('T', 1e12)
        ]
        
        # Finde bestes Präfix (Wert sollte zwischen 0.1 und 1000 liegen)
        best_prefix = ''
        best_factor = 1
        best_value = magnitude
        
        for prefix, factor in prefixes:
            test_value = magnitude / factor
            if 0.1 <= test_value <= 1000:
                if abs(test_value - 1) < abs(best_value - 1):  # Näher an 1
                    best_prefix = prefix
                    best_factor = factor
                    best_value = test_value
        
        # Optimierte Einheit erstellen
        optimized_unit_str = f"{best_prefix}m"
        try:
            optimized_unit = ureg(optimized_unit_str)
            return si_quantity.to(optimized_unit)
        except:
            return si_quantity
            
    except Exception:
        return si_quantity

def optimize_pressure_unit(si_quantity: pint.Quantity, reference_unit_str: str) -> pint.Quantity:
    """
    Optimiert Druckeinheiten basierend auf Größenordnung.
    """
    try:
        magnitude = si_quantity.magnitude  # in Pascal
        
        # Bestimme beste Druckeinheit
        if magnitude >= 1e9:  # >= 1 GPa
            return si_quantity.to(ureg.gigapascal)
        elif magnitude >= 1e6:  # >= 1 MPa
            return si_quantity.to(ureg.megapascal)
        elif magnitude >= 1e5:  # >= 100 kPa (≈ 1 bar)
            return si_quantity.to(ureg.bar)
        elif magnitude >= 1e3:  # >= 1 kPa
            return si_quantity.to(ureg.kilopascal)
        else:  # < 1 kPa
            return si_quantity.to(ureg.pascal)
            
    except Exception:
        return si_quantity

def optimize_area_unit(si_quantity: pint.Quantity, reference_unit_str: str) -> pint.Quantity:
    """
    Speziell für Flächeneinheiten optimierte Ausgabe.
    
    Args:
        si_quantity: Flächenwert in m²
        reference_unit_str: Original-Längeneinheit (z.B. "mm")
        
    Returns:
        pint.Quantity mit optimierter Flächeneinheit
    """
    try:
        magnitude = si_quantity.magnitude  # in m²
        
        # Bestimme optimale Flächeneinheit basierend auf Größenordnung
        if magnitude >= 1e6:  # >= 1 km²
            return si_quantity.to(ureg.kilometer**2)
        elif magnitude >= 1:  # >= 1 m²
            return si_quantity.to(ureg.meter**2)
        elif magnitude >= 0.01:  # >= 1 dm²
            return si_quantity.to(ureg.decimeter**2)
        elif magnitude >= 0.0001:  # >= 1 cm²
            return si_quantity.to(ureg.centimeter**2)
        else:  # < 1 cm²
            return si_quantity.to(ureg.millimeter**2)
            
    except Exception:
        return si_quantity

def validate_inputs_have_units(**kwargs) -> Dict[str, Any]:
    """
    Validiert, dass alle Eingabe-Parameter Einheiten haben.
    
    Args:
        **kwargs: Parameter-Dictionary
        
    Returns:
        Dict mit konvertierten SI-Werten und Original-Einheiten
        
    Raises:
        UnitsError: Wenn Parameter ohne Einheiten gefunden werden
    """
    result = {}
    
    for param_name, value in kwargs.items():
        if value is None:
            continue
            
        if not isinstance(value, str):
            raise UnitsError(
                f"Parameter '{param_name}' muss als String mit Einheit angegeben werden (z.B. '5.2 mm'). "
                f"Erhalten: {value} ({type(value)})"
            )
        
        # Konvertiere zu SI
        si_quantity = convert_to_si(value)
        
        # Speichere SI-Wert und Original-Einheit
        _, original_unit = parse_value_with_unit(value)
        result[param_name] = {
            'si_value': si_quantity.magnitude,
            'si_unit': str(si_quantity.units),
            'original_unit': original_unit,
            'quantity': si_quantity
        }
    
    return result 