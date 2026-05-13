# P2-S7 - GRUPO2

# Pasos

**1. Ejecutar el script SQL en SSMS**
---
El script CreacionBaseSonoraInc.sql, contiene los logins e información de toda nuestra base. 

**2. Actualizar `config.json`**
---
Se debe reemplazar `name_server` con el nombre del equipo. 

```json
{
    "name_server": "NombreDelEquipo"
}
```

**3. Correr el script**
---
```bash
python gestor_artistas.py
```

## Estructura

```
├── .gitignore
├── config.json
├── CreacionBaseSonoraInc.sql
└── gestor_artistas.py
```
