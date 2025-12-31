"""
API маршруты для работы с товарами.
CRUD-операции для номенклатуры.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db.database import get_db
from core.dependencies import get_current_user
from models import User, Product
from schemas import ProductCreate, ProductUpdate, ProductRead, ProductList

router = APIRouter(prefix="/products", tags=["Товары"])


@router.get("", response_model=ProductList)
def get_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="Поиск по названию или артикулу"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    is_active: Optional[int] = Query(None, description="Фильтр по статусу (1/0)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список товаров с пагинацией."""
    query = db.query(Product)
    
    # Поиск по названию или артикулу
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(pattern)) | 
            (Product.sku.ilike(pattern))
        )
    
    # Фильтр по категории
    if category:
        query = query.filter(Product.category == category)
    
    # Фильтр по активности
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    
    total = query.count()
    
    offset = (page - 1) * per_page
    products = query.order_by(Product.name).offset(offset).limit(per_page).all()
    
    return ProductList(
        items=products,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить товар по ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    
    return product


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать новый товар."""
    # Проверяем уникальность артикула, если указан
    if product_data.sku:
        existing = db.query(Product).filter(Product.sku == product_data.sku).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Товар с таким артикулом уже существует"
            )
    
    product = Product(**product_data.model_dump())
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить товар."""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    
    # Проверяем уникальность нового артикула
    if product_data.sku:
        existing = db.query(Product).filter(
            Product.sku == product_data.sku,
            Product.id != product_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Товар с таким артикулом уже существует"
            )
    
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить товар (или перевести в архив)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден"
        )
    
    # Вместо удаления переводим в архив
    product.is_active = 0
    db.commit()
