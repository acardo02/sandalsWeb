from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from app.models.user_model import User
from app.models.product_model import Product
from app.schemas.product_schema import ProductCreate, ProductResponse, ProductUpdate
from app.core.dependencies import get_current_admin_user

router = APIRouter()

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    current_user: User = Depends(get_current_admin_user)
):
    product_exists = await Product.find_one(Product.sku ==  product_in.sku)
    print(product_exists)
    if product_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un producto con el SKU: {product_in.sku}"
        )
    new_product = Product(**product_in.model_dump())
    await new_product.create()
    return new_product

@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El producto no existe"
        )
    await product.delete()
    return None

@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Producto no encontrado"
        )
    
    if product_update.sku is not None and product_update.sku != product.sku:
        sku_exists = await Product.find_one(Product.sku == product_update.sku)
        if sku_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El SKU '{product_update.sku}' ya está en uso por otro producto"
            )

    update_data = product_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product, field, value)

    await product.save()

    return product

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    category: Optional[str] = None,
    limit: int = 20,
    skip: int = 0
):
    query = Product.find_all()

    if category:
        query = Product.find(Product.category == category)

    products = await query.sort(-Product.created_at).skip(skip).limit(limit).to_list()

    return products
    

@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_details(product_id: str):
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El producto no existe"
        )
    return product