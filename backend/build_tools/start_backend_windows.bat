@echo off
setlocal
if exist app_config.json (
  echo Using app_config.json
)
what_the_law_backend.exe
if errorlevel 1 (
  echo.
  echo Backend exited with error. Press any key to close.
  pause > nul
)
endlocal
