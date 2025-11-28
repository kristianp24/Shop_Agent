from pydantic import BaseModel, Field
from typing import List, Optional

class InsertItem(BaseModel):
    product_name: str = Field(..., description="Name of the product to be inserted")   
    quantity: int = Field(..., description="Quantity of the product to be inserted")
    unit_price: float = Field(..., description="Unit price of the product to be inserted")
    product_code: Optional[str] = Field(None, description="Optional code of the product to be inserted")

class DeleteItem(BaseModel):
    product_name: str = Field(..., description="Name of the product to be deleted or queried")

class UpdateQuantityItem(BaseModel):
    product_name: str = Field(..., description="Name of the product to update quantity for")
    previous_quantity: int = Field(..., description="Current quantity of the product before update")
    quantity_to_be_added: int = Field(0, description="Quantity to be added to the current quantity")

class InsertItemsList(BaseModel):
    records: List[InsertItem] = Field(..., description="List of products to be inserted")

class DeleteItemsList(BaseModel):
    product_names: List[DeleteItem] = Field(..., description="List of products to be deleted")

class UpdateQuantityItemsList(BaseModel):
    records: List[UpdateQuantityItem] = Field(..., description="List of products to update quantity for")