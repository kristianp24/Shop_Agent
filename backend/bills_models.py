from pydantic import BaseModel, Field
from typing import List, Optional

class BillItem(BaseModel):
    product_name: str = Field(..., description="Name of the product")   
    quantity: int = Field(..., description="Quantity of the product purchased")
    unit_price: float = Field(..., description="Unit price of the product")
    total_price: float = Field(..., description="Total price for the quantity of the product")

class Bill(BaseModel):
    date: str = Field(..., description="Date of the bill in DD-MM-YYYY format")
    customer_name: Optional[str] = Field(None, description="Name of the customer")
    items: List[BillItem] = Field(..., description="List of items in the bill")
    total_amount: float = Field(..., description="Total amount for the bill")
    recipient_contact: Optional[str] = Field(None, description="Phone number of the recipient for WhatsApp delivery")