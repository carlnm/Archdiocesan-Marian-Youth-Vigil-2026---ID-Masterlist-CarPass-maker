from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
import os

# -------------------------------------------------------------------
# CONFIGURATION: 3.5m x 3m Wall Dimensions (7:6 Aspect Ratio)
# -------------------------------------------------------------------
SLIDE_WIDTH_INCHES = 14.0
SLIDE_HEIGHT_INCHES = 12.0

FONT_NAME = "Montserrat"
FONT_SIZE = Pt(48)
LINE_SPACING = 1.25
BG_COLOR = RGBColor(0, 0, 0)         # Pitch black
TEXT_COLOR = RGBColor(255, 255, 255) # High-contrast white


def create_praise_presentation(lyrics_text, output_filename="worship_slides.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_WIDTH_INCHES)
    prs.slide_height = Inches(SLIDE_HEIGHT_INCHES)
    blank_layout = prs.slide_layouts[6]

    # Stanzas separated by double blank lines
    stanzas = [s.strip() for s in lyrics_text.strip().split("\n\n") if s.strip()]

    for stanza in stanzas:
        slide = prs.slides.add_slide(blank_layout)

        # Set slide background to black
        background = slide.background
        fill = background.fill
        fill.solid()
        fill.fore_color.rgb = BG_COLOR

        # Safe margins
        margin_x = Inches(1.4)
        margin_y = Inches(1.5)
        box_width = Inches(SLIDE_WIDTH_INCHES - 2.8)
        box_height = Inches(SLIDE_HEIGHT_INCHES - 3.0)

        tx_box = slide.shapes.add_textbox(margin_x, margin_y, box_width, box_height)
        tf = tx_box.text_frame
        tf.word_wrap = True
        
        # 1. VERTICAL CENTERING (Anchor to the middle of the text frame)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        lines = stanza.split("\n")
        for i, line in enumerate(lines):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.text = line.strip()
            
            # 2. HORIZONTAL CENTERING
            p.alignment = PP_ALIGN.CENTER
            
            p.line_spacing = LINE_SPACING
            p.font.name = FONT_NAME
            p.font.size = FONT_SIZE
            p.font.bold = True
            p.font.color.rgb = TEXT_COLOR

    prs.save(output_filename)
    print(f"Successfully generated {len(stanzas)} centered slides -> '{output_filename}'")


# -------------------------------------------------------------------
# USAGE WITH "PRAISE" (Elevation Worship)
# -------------------------------------------------------------------
Title = "One Way"
worship_lyrics = """
I lay my life down at Your feet
'Cause You're the only One I need

I turn to You and You are always there
In troubled times it's You I seek

I put You first that's all I need
I humble all I am all to You

One way, Jesus
You're the only One that I could live for

One way, Jesus
You're the only One that I could live for

You are always, always there
Every how and every where

Your grace abounds so deeply within me
You will never, ever change

Yesterday, today the same
Forever 'til forever meets no end

One way, Jesus
You're the only One that I could live for

One way, Jesus
You're the only One that I could live for

One way, Jesus
You're the only One that I could live for

One way, Jesus
You're the only One that I could live for

You are the Way, the Truth and the Life
We live by faith and not by sight for You
We're living all for You

You are the Way, the Truth and the Life
We live by faith and not by sight for You
We're living all for You

You are the Way, the Truth and the Life
We live by faith and not by sight for You
We're living all for You

You are the Way, the Truth and the Life
We live by faith and not by sight for You
We're living all for You

One way, Jesus
You're the only One that I could live for

One way, Jesus
You're the only One that I could live for

One way, Jesus
You're the only One that I could live for

One way, Jesus
You're the only One that I could live for
"""

if __name__ == "__main__":

    os.makedirs("Youth Jam", exist_ok=True)

    output_path = f"Youth Jam/{Title}.pptx"
    create_praise_presentation(worship_lyrics, output_path)