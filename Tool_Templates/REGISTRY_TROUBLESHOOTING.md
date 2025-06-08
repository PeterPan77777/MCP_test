# Registry-Discovery Troubleshooting

## Häufigster Fehler: Variable nicht definiert

**Fehlermeldung:**
```
ERROR: Failed to load metadata: name 'grundseite_a' is not defined
```

**Ursache:** Parameter-Dictionary verwendet Variablen statt Konstanten

**Falsch:**
```python
"parameters": {
    grundseite_a: PARAMETER_GRUNDSEITE_A,  # Variable existiert nicht!
}
```

**Richtig:**
```python
"parameters": {
    FUNCTION_PARAM_2_NAME: PARAMETER_GRUNDSEITE_A,  # Konstante verwenden!
}
```

## Diagnose-Schritte

1. Server starten: `python server.py`
2. Log prüfen: SUCCESS vs ERROR Meldungen
3. Templates nutzen - sind bereits korrekt!

Alle Templates in Tool_Templates/ sind korrigiert und funktionsfähig. 