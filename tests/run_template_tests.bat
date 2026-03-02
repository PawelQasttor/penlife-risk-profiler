@echo off
REM Test text fitting with actual template and varying text lengths

echo Activating virtual environment...
call ..\venv\Scripts\activate.bat

echo.
echo Testing text fitting with actual template...
echo This will generate 4 PDFs with different text lengths
echo.

python test_template_fitting.py

echo.
echo Done! Check the output folder.
echo.

pause
