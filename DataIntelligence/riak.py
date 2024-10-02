import sys
import platform

# Obtener versión de Python y detalles del sistema
python_version = sys.version
system_info = platform.uname()

# Detalles del plugin (completa manualmente si es necesario)
obsidian_version = "v1.6.7"
code_emitter_version = "0.3.2"

# Formatear y mostrar información completa
print(f"""
Información del Sistema:
------------------------
- Sistema Operativo: {system_info.system}
- Versión de Sistema: {system_info.release}
- Máquina: {system_info.machine}

Detalles del Entorno de Obsidian:
---------------------------------
- Versión de Obsidian: {obsidian_version}
- Versión de Code Emitter: {code_emitter_version}

Detalles de Python:
-------------------
- Versión de Python: {python_version}
""")
