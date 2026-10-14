"""AI AGENT GUIDE
Purpose: Preserve the historical launcher path while forwarding startup to the
desktop interface module.
Boundary: Keep this compatibility entry point small; put presentation in
interfaz.py and reusable operations in the two standalone motor modules.
Extension contract: Existing batch files may continue executing buscador.py.
"""
from interfaz import main

if __name__ == "__main__":
    main()
