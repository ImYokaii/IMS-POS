from django.db import models
from inventory_view.models import Product
from procurement_view.models import PurchaseOrderItem
from .utils import automatic_po_generator

class ProductInstance(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='instances')
    name = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.PositiveIntegerField()
    brand = models.CharField(max_length=100, blank=True, null=True)
    reorder_level = models.PositiveIntegerField(blank=True, null=True, default=0)
    is_favorite = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.product.name} (Qty. {self.quantity}) - {self.category}"
    
    @classmethod
    def add_or_update_instance(cls, product):
        existing_instance = cls.objects.filter(name=product.name, category=product.category, brand=product.brand).first()
        
        if existing_instance:
            existing_instance.quantity += 1
            existing_instance.save(update_fields=['quantity'])
            
        else:
            cls.objects.create(
                product=product,
                name=product.name,
                category=product.category,
                quantity=1,
                brand=product.brand,
            )
        
    @classmethod
    def subtract_instance(cls, product):
        existing_instance = cls.objects.filter(name=product.name, category=product.category, brand=product.brand).first()

        if existing_instance:
            existing_instance.quantity -= 1
            existing_instance.save(update_fields=['quantity'])
            

        if existing_instance.quantity <= existing_instance.reorder_level:
            existing_po = PurchaseOrderItem.objects.filter(product=product.name, purchase_order__status="Pending").exists()

            if not existing_po:
                automatic_po_generator(product)