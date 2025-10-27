# OCR Feature - Tips for Best Results

## Overview

Le Grimoire uses Tesseract OCR with advanced image preprocessing to extract text from recipe images. While OCR technology has improved significantly, the quality of results depends heavily on the input image.

## Recent Improvements (v2.0)

### Enhanced Image Preprocessing
- **Adaptive Thresholding**: Handles varying lighting conditions
- **Denoising**: Removes camera noise and artifacts
- **Contrast Enhancement**: Improves text visibility
- **Sharpening**: Makes text edges clearer
- **Multiple Attempts**: Tries different OCR modes and uses best result

### Better OCR Configuration
- **Multi-language Support**: French + English
- **Automatic Page Segmentation**: Handles different text layouts
- **OEM 3**: Uses best OCR engine mode (LSTM neural networks)

## Tips for Best OCR Results

### 📸 Image Quality

**DO:**
- ✅ Use good lighting (natural daylight is best)
- ✅ Take photo straight-on (not at an angle)
- ✅ Keep camera steady (avoid blur)
- ✅ Ensure text is in focus
- ✅ Use high resolution (at least 1080p)
- ✅ Clean the recipe surface (remove shadows)

**DON'T:**
- ❌ Use flash if it creates glare
- ❌ Take photos in dim lighting
- ❌ Capture at extreme angles
- ❌ Include wrinkled or folded paper
- ❌ Use low-quality camera/phone

### 📄 Text Format

**Works Best With:**
- ✅ Printed text (not handwritten)
- ✅ Clear, readable fonts
- ✅ Black text on white background
- ✅ Standard font sizes (12pt+)
- ✅ Good spacing between lines

**May Struggle With:**
- ⚠️ Handwritten recipes
- ⚠️ Fancy/decorative fonts
- ⚠️ Colored backgrounds
- ⚠️ Very small text
- ⚠️ Text over images

### 🖼️ Image Composition

**Best Practices:**
- Crop to just the recipe text
- Remove borders and margins if possible
- Avoid including non-text elements
- Ensure entire recipe is visible
- Remove any shadows or glare spots

## OCR Workflow

```
1. Upload/Capture Image
   ↓
2. Automatic Preprocessing
   - Convert to grayscale
   - Apply adaptive thresholding
   - Denoise
   - Enhance contrast
   - Sharpen
   ↓
3. OCR Extraction (Multiple Attempts)
   - Try preprocessed image
   - Try original image
   - Try alternate PSM mode
   - Use best result
   ↓
4. Display Results
   - Show original image for reference
   - Pre-fill form with extracted text
   - Allow manual corrections
```

## Using OCR Results

### Expected Behavior
- **Title**: First line of text becomes recipe title
- **Instructions**: Remaining text goes to instructions
- **Image Reference**: Original image displayed for verification

### Manual Review Required
OCR is a helpful starting point, but you should always:

1. **Check the original image** (displayed above the form)
2. **Verify extracted text** for accuracy
3. **Fix any OCR errors** (common: l/1, O/0, rn/m)
4. **Add missing sections** (ingredients, times, etc.)
5. **Format properly** before submitting

### Common OCR Errors

| OCR Reads | Should Be | Why |
|-----------|-----------|-----|
| `1` | `l` | Similar shapes |
| `0` | `O` | Similar shapes |
| `rn` | `m` | Connected letters |
| `vv` | `w` | Connected letters |
| `cl` | `d` | Poor spacing |

## Troubleshooting

### "OCR extracted nothing"
- **Cause**: Poor image quality, handwriting, or decorative fonts
- **Solution**: 
  - Retake photo with better lighting
  - Use printed recipe if possible
  - Try typing recipe manually instead

### "OCR text is gibberish"
- **Cause**: Image too blurry, extreme angle, or low contrast
- **Solution**:
  - Ensure camera is focused
  - Take photo straight-on
  - Increase lighting

### "OCR missed parts of the recipe"
- **Cause**: Text is very small, faded, or multi-column layout
- **Solution**:
  - Take closer photo of text
  - Ensure all text is visible and well-lit
  - Add missing sections manually

## Alternative Approaches

### For Handwritten Recipes
OCR doesn't work well with handwriting. Instead:
1. Use manual recipe entry (`/recipes/new/manual`)
2. Still upload image of handwritten recipe
3. Reference image while typing

### For Recipe Books
1. Take multiple photos (one per page)
2. Process each page separately
3. Combine results in manual form

### For Complex Layouts
If recipe has tables, multiple columns, or graphics:
1. OCR may not preserve layout
2. Use extracted text as starting point
3. Reformat in the manual form

## Technical Details

### Tesseract Configuration
```python
# Page Segmentation Mode (PSM)
PSM 3 = Fully automatic page segmentation
PSM 6 = Assume single uniform block of text

# OCR Engine Mode (OEM)
OEM 3 = Default (LSTM neural networks)

# Languages
fra+eng = French + English support
```

### Image Processing Pipeline
```python
1. Read image with OpenCV
2. Convert to grayscale
3. Adaptive threshold (block size 11, C=2)
4. Fast non-local means denoising
5. Contrast enhancement (factor 2.0)
6. Sharpen filter
```

## Future Improvements

Planned enhancements:
- [ ] AI-powered text extraction (GPT Vision API)
- [ ] Automatic ingredient parsing
- [ ] Recipe structure detection
- [ ] Multi-page document support
- [ ] Batch processing multiple recipes
- [ ] OCR confidence scores
- [ ] Suggested corrections

## Feedback

If OCR isn't working well for your use case:
1. Note the type of recipe (printed/handwritten/book/etc.)
2. Check the original image quality
3. Try the troubleshooting steps above
4. Report persistent issues to admin

Remember: OCR is a tool to speed up data entry, not a replacement for human review! Always verify and correct the extracted text before submitting your recipe.
