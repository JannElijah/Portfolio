# MCU-Lab — Hardware Telemetry & Pass-Fail Bench Logger

Python 3.12 + SQLite microcontroller bench telemetry parser, spec boundary validator, and lot yield reporter built for semiconductor test and hardware validation workflows.

## Key Capabilities
- **UART Frame Parser & Spec Validator (`mcu_lab/telemetry.py`):** Parses key=value serial frames (`VDD_3V3`, `VCC_5V`, `MCU_TEMP_C`, `I_DRAW_MA`), validates electrical/thermal limits, and flags out-of-spec fault channels.
- **Lot Yield Analytics (`mcu_lab/storage.py`):** Computes lot pass/fail yield percentages, peak temperatures, minimum voltage droop, and exports full CSV bench logs.

## Usage
```bash
python -m mcu_lab.cli simulate --lot LOT-2026-A --count 12
python -m mcu_lab.cli yield-report --lot-id 1
python -m mcu_lab.cli export-csv --lot-id 1 --out mcu_lot_telemetry.csv
pytest
```
