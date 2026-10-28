# La riqueza de la opcionalidad — guía en español

La edición canónica del repositorio está en inglés, orientada a lectores y colaboradores internacionales. La edición española se mantiene como versión paralela.

## Archivos principales

- [`manuscript/The_Wealth_of_Optionality_EN.pdf`](manuscript/The_Wealth_of_Optionality_EN.pdf): manuscrito principal en inglés.
- [`manuscript/La_riqueza_de_la_opcionalidad_ES.pdf`](manuscript/La_riqueza_de_la_opcionalidad_ES.pdf): manuscrito en español.
- [`docs/evidence_status.md`](docs/evidence_status.md): estado de la evidencia y límites explícitos.
- [`docs/source_material_audit.md`](docs/source_material_audit.md): auditoría de los materiales de origen.

## Reproducibilidad

Desde la raíz del repositorio:

```bash
python -m pip install -r requirements.txt
python src/audit_data.py
python src/calibrate_initial_state.py
python src/bin_diagnostics.py
python src/paper_figures.py
python -m pytest -q
```

El ABM incorpora ahora una restricción de producción: las ventas realizadas no superan la producción factible con los insumos financiados antes de producir. Sigue siendo un laboratorio de mecanismos estilizado, no una tecnología productiva estimada ni una calibración dinámica exitosa.

Las pruebas verifican funciones analíticas e invariantes de implementación seleccionados. No certifican el cierre micro–macro completo ni identifican efectos causales.

## Alcance metodológico V3
El manuscrito excluye el análisis agregado de crecimiento de PTF de PWT/WDI porque no contrasta el mecanismo de liquidez de corto plazo a nivel de firma. La sección empírica se limita a un piloto descriptivo de 52 emisoras argentinas. El archivo rotulado como multi-país fue auditado como duplicado estructural del archivo argentino y se excluye de inferencia internacional. El aumento del runway en el ABM se presenta como diagnóstico de delimitación de frontera ante sumideros de excedentes ausentes, no como resultado teórico validado. El diseño propuesto para microdatos de facturas usa una matriz de red pretratamiento y diferencias en diferencias escalonadas; no es una estimación ejecutada.
