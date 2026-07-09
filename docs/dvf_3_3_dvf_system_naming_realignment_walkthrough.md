# DVF 3-3 DVF System Naming Realignment Walkthrough

Run:

```powershell
python -B Iris\build\description\v2\tools\build\run_dvf_3_3_dvf_system_naming_realignment.py --mode all
python -B Iris\build\description\v2\tools\build\validate_dvf_3_3_dvf_system_naming_realignment.py --require-complete
python -B -m unittest Iris.build.description.v2.tests.test_dvf_3_3_dvf_system_naming_realignment
```

This route is governance-only. Runtime and package surfaces are protected no-mutation surfaces.
