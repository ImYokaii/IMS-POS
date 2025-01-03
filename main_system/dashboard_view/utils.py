# ===== AUTOMATIC PO GENERATOR (WHEN LOW STOCK) ===== #
def automatic_po_generator(product):
    from procurement_view.models import PurchaseOrder, PurchaseOrderItem

    purchase_order = PurchaseOrder.objects.create(
        supplier=None, 
        buyer_company_name="Default Company", 
        buyer_address="Default Address",
    )
    
    PurchaseOrderItem.objects.create(
        purchase_order=purchase_order,
        product=product.name,
        quantity=10,
        unit_price=product.cost_price,
    )

# =============================================== #