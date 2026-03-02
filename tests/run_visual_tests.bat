@echo off
REM Helper script to run visual text fitting tests

echo Activating virtual environment...
call ..\venv\Scripts\activate.bat

echo.
echo Running visual text fitting tests...
echo.

python visual_text_test.py

echo.
echo Visual tests completed!
echo Check the output folder for generated PDFs.
echo.

pause
