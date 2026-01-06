from fastapi import APIRouter, HTTPException, status, Depends, Form, UploadFile, File
from typing import List, Optional
import random  # Importante para el random
from app.models.user_model import User
from app.services.image_service import upload_image
from app.models.product_model import Product
from app.schemas.product_schema import ProductCreate, ProductResponse, ProductUpdate
from app.core.dependencies import get_current_admin_user

router = APIRouter()

# --- CREAR PRODUCTO ---
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

# --- BORRAR PRODUCTO ---
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

# --- ACTUALIZAR PRODUCTO ---
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

# --- OBTENER PRODUCTOS (FUSIONADO: Random + Buscador) ---
@router.get("/", response_model=List[ProductResponse])
async def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 20,
    skip: int = 0,
    random_sample: bool = False
):
    # CASO 1: HOME PAGE (Random)
    # Si piden random, ignoramos búsqueda y categoría para asegurar que siempre haya datos
    if random_sample:
        all_products = await Product.find_all().to_list()
        
        if not all_products:
            return []
            
        # Si hay menos productos que el límite, devolvemos todos mezclados
        if len(all_products) <= limit:
            random.shuffle(all_products)
            return all_products
            
        # Si hay bastantes, devolvemos una muestra aleatoria
        return random.sample(all_products, limit)

    # CASO 2: PÁGINA DE PRODUCTOS (Buscador y Filtros)
    query = Product.find_all()

    # Filtro por Categoría
    if category and category != "Todos":
        query = query.find(Product.category == category)

    # Filtro por Buscador (Nombre)
    if search:
        # Busca texto parcial, ignorando mayúsculas/minúsculas ('i')
        query = query.find({"name": {"$regex": search, "$options": "i"}})

    # Ordenamos por fecha (más nuevos primero)
    products = await query.sort(-Product.created_at).skip(skip).limit(limit).to_list()
    return products

# --- DETALLE PRODUCTO ---
@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_details(product_id: str):
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="El producto no existe"
        )
    return product