
from weasyprint import HTML
from jinja2 import Template
import io
class BillPdfCreator:
    def __init__(self, name :str, date: str, items: list, total_amount: float):
        self.name = name
        self.date = date
        self.items = items
        self.total_amount = total_amount
    
    def create_pdf(self, filename: str):
        html_template = """
    <html>
    <head>
        <style>
            body { font-family: sans-serif; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .total { font-weight: bold; text-align: right; }
        </style>
    </head>
    <body>
        <h1>Invoice</h1>
        <p><strong>Customer:</strong> {{ customer }}</p>
        <p><strong>Date:</strong> {{ date }}</p>
        
        <table>
            <tr>
                <th>Product</th>
                <th>Qty</th>
                <th>Price</th>
                <th>Total</th>
            </tr>
            {% for item in items %}
            <tr>
                <td>{{ item.product_name }}</td>
                <td>{{ item.quantity }}</td>
                <td>{{ item.unit_price }}</td>
                <td>{{ item.total_price }}</td>
            </tr>
            {% endfor %}
        </table>
        
        <p class="total">Grand Total: ${{ grand_total }}</p>
    </body>
    </html>
    """
        jinja_template = Template(html_template)
    
        final_rendered_html = jinja_template.render(
            customer=self.name,         
            date=self.date,            
            items=self.items,           
            grand_total=self.total_amount 
        )
        pdf_buffer = io.BytesIO()

        HTML(string=final_rendered_html).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)

            
        return pdf_buffer
