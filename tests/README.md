# How to Run Text Fitting Tests

## Quick Start (Windows)

### Method 1: Use the Helper Scripts (Easiest)

Just double-click one of these files:

- **`run_visual_tests.bat`** - Creates visual PDF demonstrations (no template needed)
- **`run_tests.bat`** - Runs comprehensive tests (requires template PDF)

### Method 2: Command Line

**Command Prompt:**
```cmd
cd C:\projects\penlife\penlife-risk-profiler\tests
..\venv\Scripts\activate.bat
python visual_text_test.py
```

**PowerShell:**
```powershell
cd C:\projects\penlife\penlife-risk-profiler\tests
..\venv\Scripts\Activate.ps1
python visual_text_test.py
```

**Git Bash:**
```bash
cd /c/projects/penlife/penlife-risk-profiler/tests
source ../venv/Scripts/activate
python visual_text_test.py
```

## Test Files

### 1. Visual Text Test (No Template Required)
```cmd
run_visual_tests.bat
```
**Creates:**
- `output/text_fitting_visual_comparison.pdf` - Shows 6 text fitting scenarios
- `output/text_width_measurement_guide.pdf` - Width measurement reference

**Best for:** Quick visual check of how text fitting works

### 2. Comprehensive Test Suite (Requires Template)
```cmd
run_tests.bat
```
**Creates:**
- `output/test_fitting_short.pdf` - Short text examples
- `output/test_fitting_medium.pdf` - Medium text examples
- `output/test_fitting_long.pdf` - Long text examples
- `output/test_fitting_very_long.pdf` - Very long text examples

**Best for:** Testing with actual template and real-world data

## Troubleshooting

### Error: "No module named 'fitz'"

**Cause:** Virtual environment not activated

**Solution:** Use the helper scripts (`run_tests.bat` or `run_visual_tests.bat`)

Or manually activate:
```cmd
cd C:\projects\penlife\penlife-risk-profiler
venv\Scripts\activate.bat
```

### Error: "Template not found"

**Cause:** Template PDF missing (only affects comprehensive tests)

**Solution:** Use visual tests instead:
```cmd
run_visual_tests.bat
```

The visual tests don't require the template.

### PowerShell Execution Policy Error

If you get an error about execution policy when running `.ps1` files:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try running `run_tests.ps1` again.

## Output Location

All generated PDFs are saved to:
```
C:\projects\penlife\penlife-risk-profiler\tests\output\
```

## What to Look For

### In Visual Comparison PDF:
- Blue boxes = Maximum width/height constraints
- Black text = Fitted result
- "..." = Text was truncated

### In Console Output:
- `[OK]` = Text fits within constraints
- `[!]` = Warning (truncation occurred)
- `[ERROR]` = Test failed

### Example Good Output:
```
1. Short text (fits easily)
   Result: 1 line(s)
     Line 1 [OK]: "Yes" (3 chars, 15.5pt wide)
```

### Example Truncation Warning:
```
5. Very long text
   Result: 2 line(s)
     Line 1 [OK]: "Yes, I have been working in the financial" (161.1pt wide)
     Line 2 [OK]: "services industry for over 20 years..." (144.5pt wide)
   [!] Text was truncated!
```

## Next Steps After Running Tests

1. **Review the PDFs** in the `output/` folder
2. **Check console output** for truncation warnings
3. **Adjust settings** in `pdf_filler.py` if needed:
   - Increase `max_lines` for fields with truncation
   - Adjust `y` coordinates to add more vertical space
4. **Re-run tests** to verify changes

## Quick Test Command

To quickly test if everything works:

```cmd
cd C:\projects\penlife\penlife-risk-profiler\tests
run_visual_tests.bat
```

This will generate visual PDFs in about 2-3 seconds without needing the template.
