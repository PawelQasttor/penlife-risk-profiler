# Text Fitting Test Suite

This directory contains comprehensive tests for the PDF text fitting functionality.

## Test Files

### 1. `test_text_fitting.py` - Comprehensive Test Suite
Full test suite that validates all text fitting strategies.

**What it tests:**
- Text fitting logic with various lengths (short, medium, long, very long)
- Word wrapping functionality
- Edge cases (empty strings, None values, special characters)
- PDF generation with different text lengths

**Run it:**
```bash
cd tests
python test_text_fitting.py
```

**Output:**
- Console output showing each test result
- Generated PDFs in `tests/output/` directory:
  - `test_fitting_short.pdf`
  - `test_fitting_medium.pdf`
  - `test_fitting_long.pdf`
  - `test_fitting_very_long.pdf`

### 2. `visual_text_test.py` - Visual Comparison Tool
Creates visual PDFs showing how text fitting works (no template required).

**What it creates:**
- Visual comparison of 6 different text fitting scenarios
- Width measurement guide showing text widths at different lengths

**Run it:**
```bash
cd tests
python visual_text_test.py
```

**Output:**
- `text_fitting_visual_comparison.pdf` - Shows text fitting in action
- `text_width_measurement_guide.pdf` - Reference for text widths

## Understanding the Test Results

### Text Fitting Strategies (Applied in Order)

1. **✓ Original text fits** - Used as-is
2. **✓ Reduced font size** - Font reduced (7-9pt) to fit in single line
3. **✓ Word wrapping** - Text wrapped across multiple lines
4. **⚠️ Truncation** - Text truncated with "..." (last resort)

### Console Output Symbols

- `✓` - Text fits within constraints
- `✗` - Text exceeds width (should not appear in final results)
- `⚠️` - Warning (truncation occurred)

### Example Output

```
1. Long text (needs wrapping)
   Input: "Yes, I have over 10 years of experience working in financial services"
   Length: 75 characters
   Constraints: max_width=165pt, font_size=9pt, max_lines=2
   Result: 2 line(s)
     Line 1 [✓]: "Yes, I have over 10 years of experience working in" (51 chars, 164.2pt wide)
     Line 2 [✓]: "financial services" (18 chars, 56.8pt wide)
```

## Customizing Tests

### Add Custom Test Cases

Edit `test_text_fitting.py` and add to the `test_cases` list:

```python
{
    "name": "Your test case name",
    "text": "Your test text here",
    "max_width": 165,
    "font_size": 9,
    "max_lines": 2
}
```

### Test with Your Own Data

Create sample data in `test_text_fitting.py`:

```python
data = create_sample_data("long")  # Options: short, medium, long, very_long

# Or create custom data
data = RiskProfileData(
    client_info=ClientInfo(...),
    knowledge_experience=KnowledgeExperience(
        relevant_profession="Your custom answer here",
        ...
    ),
    ...
)
```

## Interpreting Visual Test PDFs

### Visual Comparison PDF
- **Blue boxes** = Maximum width/height constraint
- **Black text** = Fitted result
- **"..."** = Text was truncated

### Measurement Guide PDF
- Shows actual pixel widths of common text samples
- Reference boxes at standard widths (100pt, 165pt, 200pt, 300pt, 500pt)

## Troubleshooting

### Template not found error
```
❌ Template not found at: C:\projects\penlife\templates\PenLife Risk Profiler.pdf
```
**Solution:** `test_text_fitting.py` requires the actual template. Use `visual_text_test.py` instead, which doesn't need the template.

### Text still truncating
**Check:**
1. `max_lines` value - increase if needed
2. `max_width` value - verify it matches the actual box width
3. Spacing between fields - ensure there's room for multiple lines

### Text overlapping on PDF
**Solution:** Increase the `y` coordinate spacing between fields in `pdf_filler.py`:

```python
# Before (too tight)
"q1": {"x": 379, "y": 136, "size": 9, "max_width": 165, "max_lines": 2},
"q2": {"x": 379, "y": 159, "size": 9, "max_width": 165, "max_lines": 2},  # 23px gap

# After (more space)
"q1": {"x": 379, "y": 136, "size": 9, "max_width": 165, "max_lines": 2},
"q2": {"x": 379, "y": 170, "size": 9, "max_width": 165, "max_lines": 2},  # 34px gap
```

## Quick Reference

### Recommended max_lines by Field Type

| Field Type | Recommended max_lines | Rationale |
|------------|----------------------|-----------|
| Yes/No answers | 1 | Short responses |
| Multiple choice | 1-2 | Usually brief |
| Short text | 2 | Handles most cases |
| Long text | 3-4 | Detailed explanations |
| Names/dates | 1 | Always short |

### Recommended max_width by Box Size

| Box Width (visual) | max_width (pt) | Typical Use |
|-------------------|----------------|-------------|
| Small box | 100-150 | Checkboxes, short fields |
| Medium box | 150-200 | Standard answer fields |
| Large box | 200-350 | Long-form text |
| Full width | 500+ | Paragraphs, descriptions |

## Best Practices

1. **Always run tests after coordinate changes** - Verify text still fits
2. **Test with real data** - Use actual long answers from clients
3. **Check all text lengths** - Test short, medium, long, and very long
4. **Review visual PDFs** - Ensure no overlap or truncation
5. **Log truncation warnings** - Monitor for fields that need adjustment

## Next Steps

After running tests:

1. Review generated PDFs in `tests/output/`
2. Check console output for truncation warnings
3. Adjust `max_lines` or `max_width` as needed
4. Re-run tests to verify fixes
5. Test with real client data before production use
