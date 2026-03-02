@echo off
REM Helper script to run text fitting tests with virtual environment activated

echo Activating virtual environment...
call ..\venv\Scripts\activate.bat

echo.
echo Running text fitting tests...
echo.

python test_text_fitting.py

echo.
echo Tests completed!
echo Check the output folder for generated PDFs.
echo.

pause
