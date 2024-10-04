from flask import Flask, render_template, send_file, request
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import chess
import chess.pgn

app = Flask(__name__)


# Route to render the chessboard page
@app.route("/")
def index():
    return render_template("index.html")


# Route to generate the chessboard PDF
@app.route("/download_pdf")
def download_pdf():
    # Get the chess moves from the query string
    moves_input = request.args.get("moves", "")

    # Create a chess board
    board = chess.Board()

    # Parse the moves from the user input
    try:
        game = chess.pgn.Game()
        node = game
        for move in moves_input.split():
            if move[0].isdigit():
                continue  # Skip move numbers
            move = move.replace(".", "")  # Remove any periods
            move_obj = board.parse_san(move)
            node = node.add_variation(move_obj)
            board.push(move_obj)
    except Exception as e:
        print(f"Error parsing moves: {e}")
        return "Invalid chess moves"

    # Create an in-memory bytes buffer for the PDF
    buffer = BytesIO()

    # Set up canvas for the PDF file (A4 size)
    c = canvas.Canvas(buffer, pagesize=A4)
    page_width, page_height = A4  # A4 dimensions (595.28 x 841.89 in points)

    # Fill the entire page with the background color
    c.setFillColor(colors.black)
    print("black")
    c.rect(0, 0, page_width, page_height, fill=True, stroke=False)

    # Define chessboard size (90% of the page's width)
    chessboard_size = page_width * 0.9  # Chessboard takes 90% of the width
    square_size = chessboard_size / 8  # Each square is 1/8th of the chessboard size

    # Calculate the left margin and top margin for the chessboard
    margin_left = (page_width - chessboard_size) / 2
    margin_top = page_height - 100  # Move the chessboard 150 points down from the top

    # Draw the final chessboard state after applying the moves
    for row in range(8):
        for col in range(8):
            # Calculate the square index
            square = chess.square(col, 7 - row)  # Flip row for correct orientation

            # Determine the piece on the square
            piece = board.piece_at(square)
            if (row + col) % 2 == 0:
                color = colors.white  # Light square
            else:
                color = colors.black  # Dark square

            # Set the fill color for the square
            c.setFillColor(color)
            c.rect(
                margin_left + col * square_size,
                margin_top - row * square_size,
                square_size,
                square_size,
                fill=True,
                stroke=False,
            )

            # If there's a piece on the square, draw it (for now, we'll just mark it)
            if piece:

                c.setFillColor(colors.white)
                """c.setFont("Helvetica", 14)
                c.drawCentredString(
                    margin_left + col * square_size + square_size / 2,
                    margin_top - row * square_size + square_size / 3,
                    piece.symbol().upper(),
                )
                """
                c.rect(
                    margin_left + col * square_size,
                    margin_top - row * square_size,
                    square_size,
                    square_size,
                    fill=True,
                    stroke=False,
                )

    # Register the external TTF font
    font_path = "static/PublicSans_Complete/Fonts/TTF/PublicSans-Variable.ttf"  # Path to your font file
    pdfmetrics.registerFont(
        TTFont("PublicSans-ExtraBold", font_path)
    )  # Register font with a name

    # Now, add the title under the chess grid
    title_text = "M A D E  B Y  G E R O R G E . S T U D I O"

    # Calculate the position for the title below the chessboard
    title_y_position = (
        margin_top - chessboard_size + 35
    )  # 50 points below the chessboard

    # Set the font for the title and draw it
    c.setFont("PublicSans-ExtraBold", 7.79)  # Use your custom font
    c.setFillColor(colors.white)  # Set title color to black
    c.drawCentredString(page_width / 6, title_y_position, title_text)

    # Finalize the PDF
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


"""
 e4 e5 f4 exf4 Bc4 Qh4+ Kf1 b5 Bxb5 Nf6 Nf3 Qh6 d3 Nh5 Nh4 Qg5 Nf5 c6 g4 Nf6 Rg1 cxb5 h4 Qg6 h5 Qg5 Qf3 Ng8 Bxf4 Qf6 Nc3 Bc5 Nd5 Qxb2 Bd6 Bxg1 e5 Qxa1+ Ke2 Na6 Nxg7+ Kd8 Qf6+ Nxf6 Be7#

"""

if __name__ == "__main__":
    app.run(debug=True)
