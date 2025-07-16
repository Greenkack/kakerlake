# File: /pv-calculations-visualizer/pv-calculations-visualizer/src/pdf/styles.py

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Define custom styles for the PDF
styles = getSampleStyleSheet()

# Custom styles
styles.add(ParagraphStyle(
    name='Heading1',
    fontSize=24,
    spaceAfter=12,
    textColor=colors.black,
    alignment=1,  # Centered
))

styles.add(ParagraphStyle(
    name='Heading2',
    fontSize=18,
    spaceAfter=10,
    textColor=colors.black,
    alignment=1,  # Centered
))

styles.add(ParagraphStyle(
    name='NormalLeft',
    fontSize=12,
    spaceAfter=6,
    textColor=colors.black,
    alignment=0,  # Left aligned
))

styles.add(ParagraphStyle(
    name='TableLabel',
    fontSize=12,
    textColor=colors.black,
    alignment=0,  # Left aligned
    spaceAfter=4,
))

styles.add(ParagraphStyle(
    name='TableText',
    fontSize=12,
    textColor=colors.black,
    alignment=0,  # Left aligned
    spaceAfter=4,
))

styles.add(ParagraphStyle(
    name='TableTextSmall',
    fontSize=10,
    textColor=colors.grey,
    alignment=0,  # Left aligned
    spaceAfter=4,
))

styles.add(ParagraphStyle(
    name='SubSectionTitle',
    fontSize=14,
    textColor=colors.black,
    alignment=0,  # Left aligned
    spaceAfter=8,
))