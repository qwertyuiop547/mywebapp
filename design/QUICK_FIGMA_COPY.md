# Quick Figma Copy Guide

## Step 1: Import Tokens (2 minutes)
1. Figma → Plugins → Tokens Studio → Tokens tab
2. Menu (…) → Import → JSON
3. Copy ALL content from `design/tokens.json` → Paste → Import
4. Click "Styles & Variables" → Create styles → Create

## Step 2: Copy These Exact Values

### Glass Panel (Base Card)
- Frame: 400×300, Auto Layout Vertical
- Fill: Linear gradient
  - Start: rgba(255,255,255,0.30)
  - End: rgba(255,255,255,0.15)
- Stroke: 1px rgba(255,255,255,0.20)
- Radius: 20
- Effects:
  - Drop shadow: 0, 8, 32, rgba(0,0,0,0.30)
  - Inner shadow: 0, 1, 0, rgba(255,255,255,0.40)
  - Background blur: 20px
- Text color: #ffffff

### Primary Button
- Frame: Auto Layout Horizontal, padding 16×32
- Fill: #003f7f
- Radius: 12
- Text: white, bold
- Effects: Drop shadow 0, 4, 20, rgba(0,0,0,0.15)

### Secondary Button
- Same as Primary but Fill: #0038a8

### Input Field
- Frame: 400×50, padding 12×16
- Fill: rgba(255,255,255,0.90)
- Stroke: 2px rgba(255,255,255,0.30)
- Radius: 12
- Text: #1f2937

### Status Badge
- Pending: bg #fde68a, text #92400e
- Approved: bg #10b981, text #ffffff
- Radius: 50 (pill)

## Step 3: Build Pages (Copy-Paste Layout)

### Home Page
1. Background: Your barangay photo + black overlay 30%
2. Glass Panel (centered) with:
   - Title: "Barangay Complaint Portal" (white, large)
   - Subtitle: "Serbisyong Mabilis, Solusyong Tapat" (white 90%)
   - Primary Button: "File a Complaint"
   - Secondary Button: "Submit Feedback"

### User Approval Page
1. Glass Panel with:
   - Header: Avatar circle + Name + "RESIDENT" badge
   - Body: Two columns
     - Left: Email, Username, Registration Date, Status
     - Right: Profile photo preview
   - Footer: "APPROVE" + "REJECT" buttons

### Submit Feedback Page
1. Glass Panel with sections:
   - Basic Information: Feedback Type dropdown + Rating stars
   - Detailed Feedback: Title + Comment textarea
   - Supporting Documents: File upload box (dashed border)
   - Privacy: Anonymous checkbox
   - Submit button (full width)

### Create Complaint Page
1. Glass Panel with left border 6px blue
2. Form fields: Category, Title, Description, Location, Priority
3. Anonymous section (yellow background)
4. Submit button (full width)

## Step 4: Prototype Flow
- Home → "File a Complaint" → Login → Create Complaint
- User Approval → Approve/Reject → Confirmation overlay

## Quick Tips
- Use Auto Layout everywhere
- Copy-paste these exact rgba values
- Name components: "Card/Glass", "Button/Primary", etc.
- Make variants for hover/pressed states

Done! You now have the complete system in Figma.
