from flask import Flask, render_template, send_file
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas

app = Flask(__name__)


# Route to render the chessboard page
@app.route("/")
def index():
    return render_template("index.html")


# Route to generate the chessboard PDF
@app.route("/download_pdf")
def download_pdf():
    # Create an in-memory bytes buffer for the PDF
    buffer = BytesIO()

    # Set up canvas for the PDF file (A4 size)
    c = canvas.Canvas(buffer, pagesize=A4)
    page_width, page_height = A4  # A4 dimensions (595.28 x 841.89 in points)

    # Define chessboard size (matching the size from the PDF)
    chessboard_size = page_width * 0.9  # Assume the grid takes 80% of the page's width
    square_size = chessboard_size / 8  # Each square is 1/8th of the chessboard size

    # Calculate the margins and starting position to center the chessboard
    margin_left = (page_width - chessboard_size) / 2
    margin_top = (
        page_height + chessboard_size+125
    ) / 2  # Top Y position for the first square

    # Draw the 8x8 chessboard
    for row in range(8):
        for col in range(8):
            # Alternate square colors
            if (row + col) % 2 == 0:
                color = colors.white
            else:
                color = colors.black

            # Set the fill color and draw the square (no stroke/border)
            c.setFillColor(color)
            c.rect(
                margin_left + col * square_size,
                margin_top - row * square_size,
                square_size,
                square_size,
                fill=True,
                stroke=False,
            )

    # Finalize the PDF file
    c.save()

    # Move the buffer position to the beginning
    buffer.seek(0)

    # Return the generated PDF file as a downloadable file
    return send_file(
        buffer,
        as_attachment=True,
        download_name="chessboard.pdf",
        mimetype="application/pdf",
    )


if __name__ == "__main__":
    app.run(debug=True)
