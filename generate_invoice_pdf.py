from fpdf import FPDF
import json

# Load the sample JSON data
with open("sample_invoice.json") as f:
    data = json.load(f)

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

pdf.cell(200, 10, txt="Invoice", ln=True, align="C")
pdf.ln(10)

pdf.cell(100, 10, txt=f"Invoice Number: {data['invoice_number']}", ln=True)
pdf.cell(100, 10, txt=f"Date: {data['date']}", ln=True)
pdf.cell(100, 10, txt=f"Vendor: {data['vendor']}", ln=True)
pdf.cell(100, 10, txt=f"Total: ${data['total']}", ln=True)
pdf.ln(10)

pdf.cell(100, 10, txt="Line Items:", ln=True)
for item in data['line_items']:
    pdf.cell(100, 10, txt=f"- {item['desc']}: Qty {item['qty']} @ ${item['price']}", ln=True)

pdf.output("sample_invoice.pdf")
print("PDF generated: sample_invoice.pdf")
