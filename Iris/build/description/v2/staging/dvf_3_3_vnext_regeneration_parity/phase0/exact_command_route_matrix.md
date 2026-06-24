# Exact Command Route Matrix

Status: route locked for DVF 3-3 vNext regeneration parity.

| Phase | Role | Command | Expected |
| --- | --- | --- | --- |
| phase0 | common_validation | `python -B Iris/build/description/v2/tools/build/run_dvf_3_3_vnext_regeneration_parity.py --phase phase0` | 0 |
| phase1 | fresh_full_rerun | `python -B Iris/build/description/v2/tools/build/run_dvf_3_3_vnext_regeneration_parity.py --phase phase1` | 0 |
| phase2 | fresh_full_rerun | `python -B Iris/build/description/v2/tools/build/run_dvf_3_3_vnext_regeneration_parity.py --phase phase2` | 0 |
| phase3 | fresh_full_rerun | `python -B Iris/build/description/v2/tools/build/run_dvf_3_3_vnext_regeneration_parity.py --phase phase3` | 0 |
| phase4 | common_validation | `python -B Iris/build/description/v2/tools/build/run_dvf_3_3_vnext_regeneration_parity.py --phase phase4` | 0 |
| phase5 | common_validation | `python -B Iris/build/description/v2/tools/build/run_dvf_3_3_vnext_regeneration_parity.py --phase phase5` | 0 |
| phase6 | fresh_full_rerun | `python -B Iris/build/description/v2/tools/build/run_dvf_3_3_vnext_regeneration_parity.py --phase phase6` | 0 |
| phase7 | common_validation | `python -B Iris/build/description/v2/tools/build/run_dvf_3_3_vnext_regeneration_parity.py --phase phase7` | 0 |
| validation | common_validation | `powershell -ExecutionPolicy Bypass -File .\tools\check_lua_syntax.ps1 -Roots Iris\build\description\v2\staging\dvf_3_3_vnext_regeneration_parity\phase3\chunks` | 0 |
