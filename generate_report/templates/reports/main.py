from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import portrait
from reportlab.platypus import Image

filename = "new.pdf"

Phrase = "muslimban"

terms = ["Habibi", "Abu Dhabhi", "Mosque"]

c = canvas.Canvas(filename, pagesize=portrait(letter))

# Header
c.setFont("Helvetica", 30, leading=None)
c.drawString(180, 740, "Phrase: " + Phrase)

# Terms
c.setFont("Helvetica", 24, leading=None)
c.drawCentredString(300, 690, "Related Terms: Habibi,Abu Dhabhi,Mosque")


# TWITTER SPHERE IMPORTANCE
image = "weights.jpeg"
c.setFont("Helvetica", 18, leading=None)
c.drawCentredString(300, 630, "Twittersphere Importance over time")
c.drawImage(image, 120, 350, width=370, height=270)

# FREQUENCY OF usage
image = "frequency.jpeg"
c.setFont("Helvetica", 18, leading=None)
c.drawCentredString(300, 300, "frequency of usage")
c.drawImage(image, 120, 20, width=370, height=270)

c.showPage()

# SENTIMENTS
image = "sentiments.jpeg"
c.setFont("Helvetica", 18, leading=None)
c.drawCentredString(300, 740, "Sentiments of the Twitter Audience")
c.drawImage(image, 120, 460, width=370, height=270)

# PIE CHART
c.setFont("Helvetica", 18, leading=None)
c.drawCentredString(300, 410, "General Sentiments of the Public over the entire period")
pie = "pie.jpeg"
c.drawImage(pie, 150, 130, width=300, height=270)
c.showPage()

c.save()
