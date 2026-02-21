#!/usr/bin/env python3
"""Script principal de lanzamiento para el Sistema Brackets.
Este archivo actúa como punto de entrada desde la raíz del proyecto.
"""

import sys
import os

# Agregar el directorio brackets al path para importaciones
brackets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'brackets')
if brackets_dir not in sys.path:
    sys.path.insert(0, brackets_dir)

# Importar y ejecutar el main desde brackets
from brackets.main import main

if __name__ == "__main__":
    main()
