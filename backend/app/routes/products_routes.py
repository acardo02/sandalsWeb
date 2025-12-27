from fastapi import APIRouter, HTTPException, status, Depends, Form, UploadFile, File
from typing import List, Optional
from app.models.user_model import User
from app.models.product_model import Product
from app.schemas.product_schema import ProductResponse, ProductUpdate
from app.core.dependencies import get_current_admin_user
from app.services.image_service import upload_image

router = APIRouter()

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    stock: int = Form(...),
    sku: str = Form(...),
    category: str = Form("General"),

    image: UploadFile = File(...),

    current_user: User = Depends(get_current_admin_user)
):
    product_exists = await Product.find_one(Product.sku == sku)
    print(product_exists)
    if product_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un producto con el SKU: {sku}"
        )
    image_url = upload_image(image)

    new_product = Product(
        name=name, 
        description=description, 
        price=price,
        stock=stock,
        sku=sku,
        category=category,
        image_url=image_url
    )
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