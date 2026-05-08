@echo off
setlocal
if exist app_config.json (
  echo Using app_config.json
)
what_the_law_backend.exe
endlocal
