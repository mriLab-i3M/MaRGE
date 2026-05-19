# Arquitectura de dependencias — GUI ↔ MaRGE

Documento generado a partir del análisis de imports del sistema.  
Punto de entrada: formularios GUI `frm_inicio` y `frm_nuevo_exp`.

---

## Módulos excluidos (importados pero NO usados)

Los siguientes módulos están importados en `marge/ui/window_main.py` pero el PDF de referencia indica que no se utilizan:

| Módulo | Clase |
|--------|-------|
| `marge.controller.controller_menu` | `MenuController` |
| `marge.controller.controller_printer` | `Printer` |
| `marge.controller.controller_sequence_list` | `SequenceListController` |
| `marge.controller.controller_sequence_inputs` | `SequenceInputsController` |
| `marge.controller.controller_postprocessing` | `ProcessingWindowController` |

---

## Árbol de dependencias

```
GUI (frm_inicio / frm_nuevo_exp)
│
├── marge/configs/
│   ├── hw_config.py          ← usado transversalmente en casi todo el sistema
│   └── units.py              ← secuencias y módulos de reconstrucción
│
├── marge/autotuning/
│   └── autotuning.py
│       └── marge/vna/Hardware.py
│           ├── VNA.py
│           │   ├── Serial.py
│           │   └── Version.py
│           ├── AVNA.py
│           │   ├── Serial.py
│           │   └── VNA.py
│           ├── NanoVNA.py
│           │   ├── Serial.py
│           │   └── Version.py
│           ├── NanoVNA_F.py
│           │   ├── NanoVNA.py
│           │   └── Serial.py
│           ├── NanoVNA_F_V2.py
│           │   ├── NanoVNA.py
│           │   └── Serial.py
│           ├── NanoVNA_H.py
│           │   ├── NanoVNA.py
│           │   └── Serial.py
│           ├── NanoVNA_H4.py
│           │   ├── Serial.py
│           │   └── NanoVNA_H.py
│           ├── NanoVNA_V2.py
│           │   ├── Serial.py
│           │   ├── VNA.py
│           │   └── Version.py
│           ├── TinySA.py
│           │   ├── Serial.py
│           │   └── VNA.py
│           └── Serial.py       ← leaf node
│
├── marge/marcos/marcos_client/
│   ├── experiment.py
│   │   ├── local_config.py     ← leaf node (parámetros de conexión)
│   │   ├── grad_board.py
│   │   │   └── local_config.py
│   │   ├── server_comms.py
│   │   │   └── marmachine.py   ← leaf node
│   │   └── marcompile.py
│   │       ├── marmachine.py
│   │       └── configs/hw_config.py
│   └── (server_comms.py también usado desde experiment_gui.py)
│
├── marge/seq/
│   ├── sequences.py            ← carga DINÁMICA de todos los .py en marge/seq/
│   │   ├── sequence_template.py
│   │   │   ├── controller/experiment_gui.py
│   │   │   ├── configs/hw_config.py
│   │   │   ├── configs/units.py
│   │   │   └── seq/mriBlankSeq.py
│   │   │
│   │   ├── mriBlankSeq.py      ← clase base de todas las secuencias
│   │   │   ├── controller/experiment_gui.py
│   │   │   ├── configs/hw_config.py
│   │   │   ├── marge_utils/utils.py
│   │   │   └── recon/data_processing.py
│   │   │
│   │   ├── rare_pp.py
│   │   │   ├── controller/experiment_gui.py
│   │   │   ├── configs/hw_config.py
│   │   │   ├── configs/units.py
│   │   │   ├── seq/mriBlankSeq.py
│   │   │   ├── marge_utils/utils.py
│   │   │   ├── marge_tyger/tyger_denoising_tep.py
│   │   │   ├── marge_tyger/tyger_denoising_local.py
│   │   │   └── marge_tyger/tyger_rare.py
│   │   │
│   │   ├── rare_double_image.py
│   │   │   ├── controller/experiment_gui.py
│   │   │   ├── configs/hw_config.py
│   │   │   ├── configs/units.py
│   │   │   ├── seq/mriBlankSeq.py
│   │   │   ├── marge_utils/utils.py
│   │   │   ├── marge_tyger/tyger_rare.py
│   │   │   ├── marge_tyger/tyger_denoising_double_tep.py
│   │   │   ├── marge_tyger/tyger_denoising_double_local.py
│   │   │   └── marge_tyger/tyger_config.py
│   │   │
│   │   ├── localizer.py
│   │   │   └── seq/rare_pp.py
│   │   │
│   │   ├── petra.py
│   │   │   ├── controller/experiment_gui.py
│   │   │   ├── configs/hw_config.py
│   │   │   └── seq/mriBlankSeq.py
│   │   │
│   │   ├── cpmg.py
│   │   │   ├── marcos/marcos_client/experiment.py
│   │   │   ├── configs/hw_config.py
│   │   │   ├── configs/units.py
│   │   │   └── seq/mriBlankSeq.py
│   │   │
│   │   ├── inversionRecovery.py
│   │   │   ├── marcos/marcos_client/experiment.py
│   │   │   ├── configs/hw_config.py
│   │   │   └── seq/mriBlankSeq.py
│   │   │
│   │   ├── noise.py
│   │   │   ├── controller/experiment_gui.py
│   │   │   ├── configs/hw_config.py
│   │   │   ├── configs/units.py
│   │   │   ├── seq/mriBlankSeq.py
│   │   │   └── marge_utils/utils.py
│   │   │
│   │   ├── rabiFlops.py
│   │   │   ├── configs/hw_config.py
│   │   │   ├── configs/units.py
│   │   │   └── seq/mriBlankSeq.py
│   │   │
│   │   └── autoTuning.py
│   │       ├── autotuning/autotuning.py
│   │       ├── configs/hw_config.py
│   │       ├── configs/units.py
│   │       └── seq/mriBlankSeq.py
│
├── marge/controller/
│   ├── controller_main.py
│   │   ├── seq/sequences.py
│   │   ├── ui/window_main.py
│   │   ├── autotuning/autotuning.py
│   │   └── configs/hw_config.py
│   │
│   ├── controller_console.py
│   │   └── widgets/widget_console.py
│   │
│   ├── controller_figures.py
│   │   ├── controller/controller_plot3d.py
│   │   ├── widgets/widget_figures.py
│   │   └── seq/sequences.py
│   │
│   ├── controller_toolbar_figures.py
│   │   └── widgets/widget_toolbar_figures.py
│   │
│   ├── controller_toolbar_marcos.py
│   │   ├── widgets/widget_toolbar_marcos.py
│   │   ├── marcos/marcos_client/experiment.py
│   │   ├── configs/hw_config.py
│   │   ├── marge_tyger/tyger_config.py
│   │   └── autotuning/autotuning.py
│   │
│   ├── controller_toolbar_protocols.py
│   │   ├── seq/sequences.py
│   │   └── widgets/widget_toolbar_protocols.py
│   │
│   ├── controller_toolbar_sequences.py
│   │   ├── controller/controller_plot3d.py
│   │   ├── controller/controller_plot1d.py
│   │   ├── seq/sequences.py
│   │   ├── widgets/widget_toolbar_sequences.py
│   │   └── configs/hw_config.py
│   │
│   ├── controller_history_list.py
│   │   ├── controller/controller_plot3d.py
│   │   ├── controller/controller_plot1d.py
│   │   ├── controller/controller_smith_chart.py
│   │   ├── widgets/widget_history_list.py
│   │   ├── manager/dicommanager.py
│   │   ├── marge_utils/utils.py
│   │   └── configs/hw_config.py
│   │
│   ├── controller_protocol_inputs.py
│   │   ├── seq/sequences.py
│   │   ├── widgets/widget_protocol_inputs.py
│   │   └── configs/hw_config.py
│   │
│   ├── controller_protocol_list.py
│   │   └── widgets/widget_protocol_list.py
│   │
│   ├── controller_plot3d.py
│   │   ├── seq/sequences.py
│   │   ├── widgets/widget_plot3d.py
│   │   └── configs/hw_config.py
│   │
│   ├── controller_plot1d.py
│   │   └── widgets/widget_plot1d.py
│   │
│   ├── controller_smith_chart.py
│   │   └── widgets/widget_smith_chart.py
│   │
│   └── experiment_gui.py
│       ├── marcos/marcos_client/experiment.py
│       ├── marcos/marcos_client/server_comms.py
│       └── configs/hw_config.py
│
├── marge/ui/
│   └── window_main.py          ← instancia todos los controllers activos
│       └── widgets/widget_custom_and_protocol.py
│
├── marge/widgets/              ← todos son leaf nodes (sin imports internos de marge)
│   ├── widget_console.py
│   ├── widget_figures.py
│   ├── widget_toolbar_figures.py
│   ├── widget_toolbar_marcos.py
│   ├── widget_toolbar_protocols.py
│   ├── widget_toolbar_sequences.py
│   ├── widget_history_list.py
│   ├── widget_protocol_inputs.py
│   ├── widget_protocol_list.py
│   ├── widget_custom_and_protocol.py
│   ├── widget_plot3d.py
│   ├── widget_plot1d.py
│   └── widget_smith_chart.py
│
├── marge/manager/
│   └── dicommanager.py         ← leaf node
│
├── marge/marge_utils/
│   └── utils.py
│       ├── manager/dicommanager.py
│       └── configs/hw_config.py
│
├── marge/recon/
│   ├── data_processing.py      ← carga DINÁMICA de todos los .py en marge/recon/
│   │   ├── RareDoubleImage.py  → configs/hw_config.py, marge_utils/utils.py
│   │   ├── Localizer.py        → configs/hw_config.py, marge_utils/utils.py
│   │   ├── Noise.py            → configs/hw_config.py
│   │   ├── Larmor.py           → configs/hw_config.py
│   │   ├── SPDS.py             → configs/hw_config.py, marge_utils/utils.py
│   │   ├── RabiFlops.py        → configs/hw_config.py
│   │   ├── RarePyPulseq.py     → configs/hw_config.py, marge_utils/utils.py
│   │   ├── TSE.py              → configs/hw_config.py
│   │   ├── Shimming.py         → configs/hw_config.py, configs/units.py
│   │   ├── Default_SeqName.py  ← leaf node
│   │   ├── InversionRecovery.py← leaf node
│   │   └── AutoTuning.py       ← leaf node
│
└── marge/marge_tyger/
    ├── tyger_config.py                         ← leaf node
    ├── tyger_rare.py
    │   ├── marge_tyger/tyger_config.py
    │   ├── marge_tyger/fromMATtoMRD3D_RARE_recon.py  ← leaf node
    │   └── marge_tyger/fromMRDtoMAT3D.py             ← leaf node
    │
    ├── tyger_denoising_tep.py
    │   ├── marge_tyger/tyger_config.py
    │   ├── marge_tyger/fromMATtoMRD3D_RARE.py         ← leaf node
    │   ├── marge_tyger/fromMATtoMRD3D_RARE_old.py     ← leaf node
    │   └── marge_tyger/fromMRDtoMAT3D_noise.py        ← leaf node
    │
    ├── tyger_denoising_local.py
    │   ├── marge_tyger/fromMATtoMRD3D_RARE_local_denoising.py  ← leaf node
    │   └── marge_tyger/fromMRDtoMAT3D_local_denoising.py       ← leaf node
    │
    ├── tyger_denoising_double_tep.py
    │   ├── marge_tyger/tyger_config.py
    │   ├── marge_tyger/fromMATtoMRD3D_RAREdouble_noise.py  ← leaf node
    │   ├── marge_tyger/fromMATtoMRD3D_RAREdouble_old.py    ← leaf node
    │   └── marge_tyger/fromMRDtoMAT3D_noise.py              ← leaf node
    │
    └── tyger_denoising_double_local.py
        ├── marge_tyger/fromMATtoMRD3D_RAREdouble_local.py  ← leaf node
        └── marge_tyger/fromMRDtoMAT3D_local_denoising.py   ← leaf node
```

---

## Resumen por módulo

| Módulo | Ficheros usados |
|--------|----------------|
| `marge/configs/` | `hw_config.py`, `units.py` |
| `marge/autotuning/` | `autotuning.py` |
| `marge/vna/` | `Hardware.py`, `VNA.py`, `AVNA.py`, `NanoVNA.py`, `NanoVNA_F.py`, `NanoVNA_F_V2.py`, `NanoVNA_H.py`, `NanoVNA_H4.py`, `NanoVNA_V2.py`, `TinySA.py`, `Serial.py`, `Version.py` |
| `marge/marcos/marcos_client/` | `experiment.py`, `local_config.py`, `grad_board.py`, `server_comms.py`, `marcompile.py`, `marmachine.py` |
| `marge/seq/` | `sequences.py`, `sequence_template.py`, `mriBlankSeq.py`, `rare_pp.py`, `rare_double_image.py`, `localizer.py`, `petra.py`, `cpmg.py`, `inversionRecovery.py`, `noise.py`, `rabiFlops.py`, `autoTuning.py` |
| `marge/controller/` | `controller_main.py`, `controller_console.py`, `controller_figures.py`, `controller_toolbar_figures.py`, `controller_toolbar_marcos.py`, `controller_toolbar_protocols.py`, `controller_toolbar_sequences.py`, `controller_history_list.py`, `controller_protocol_inputs.py`, `controller_protocol_list.py`, `controller_plot3d.py`, `controller_plot1d.py`, `controller_smith_chart.py`, `experiment_gui.py` |
| `marge/ui/` | `window_main.py` |
| `marge/widgets/` | `widget_console.py`, `widget_figures.py`, `widget_toolbar_figures.py`, `widget_toolbar_marcos.py`, `widget_toolbar_protocols.py`, `widget_toolbar_sequences.py`, `widget_history_list.py`, `widget_protocol_inputs.py`, `widget_protocol_list.py`, `widget_custom_and_protocol.py`, `widget_plot3d.py`, `widget_plot1d.py`, `widget_smith_chart.py` |
| `marge/manager/` | `dicommanager.py` |
| `marge/marge_utils/` | `utils.py` |
| `marge/recon/` | `data_processing.py`, `RareDoubleImage.py`, `Localizer.py`, `Noise.py`, `Larmor.py`, `SPDS.py`, `RabiFlops.py`, `RarePyPulseq.py`, `TSE.py`, `Shimming.py`, `Default_SeqName.py`, `InversionRecovery.py`, `AutoTuning.py` |
| `marge/marge_tyger/` | `tyger_config.py`, `tyger_rare.py`, `tyger_denoising_tep.py`, `tyger_denoising_local.py`, `tyger_denoising_double_tep.py`, `tyger_denoising_double_local.py`, `fromMATtoMRD3D_RARE_recon.py`, `fromMRDtoMAT3D.py`, `fromMATtoMRD3D_RARE.py`, `fromMATtoMRD3D_RARE_old.py`, `fromMRDtoMAT3D_noise.py`, `fromMATtoMRD3D_RARE_local_denoising.py`, `fromMRDtoMAT3D_local_denoising.py`, `fromMATtoMRD3D_RAREdouble_noise.py`, `fromMATtoMRD3D_RAREdouble_old.py`, `fromMATtoMRD3D_RAREdouble_local.py` |

---

## Notas importantes

- **Carga dinámica en `sequences.py`**: importa en tiempo de ejecución todos los `.py` de `marge/seq/` que tengan `toMaRGE=True`. Cualquier fichero nuevo en esa carpeta se incluye automáticamente.
- **Carga dinámica en `recon/data_processing.py`**: importa en tiempo de ejecución todos los módulos de `marge/recon/` para buscar funciones de reconstrucción por nombre de secuencia.
- **`hw_config.py`** es el fichero más transversal del sistema: prácticamente todos los módulos lo importan.
- **`mriBlankSeq.py`** es la clase base de todas las secuencias; cualquier cambio en ella afecta a todas.
- **`experiment_gui.py`** actúa como wrapper de `marcos_client/experiment.py` añadiendo lógica de interfaz gráfica.