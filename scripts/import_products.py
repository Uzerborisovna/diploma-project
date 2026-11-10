import os
import sys
import yaml
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from shop.models import Shop, Category, Product, ProductParameter

def import_from_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    
    shop_name = data['shop']
    shop, _ = Shop.objects.get_or_create(name=shop_name)
    
    for category_name, products in data['categories'].items():
        category, _ = Category.objects.get_or_create(name=category_name)
        category.shops.add(shop)
        
        for product_data in products:
            product, _ = Product.objects.update_or_create(
                name=product_data['name'],
                shop=shop,
                defaults={
                    'category': category,
                    'price': product_data['price'],
                    'quantity': product_data.get('quantity', 0),
                }
            )
            
            if 'parameters' in product_data:
                for param_name, param_value in product_data['parameters'].items():
                    ProductParameter.objects.update_or_create(
                        product=product,
                        name=param_name,
                        defaults={'value': param_value}
                    )
    
    print(f"Импорт из {file_path} завершен.")

if __name__ == '__main__':
    import_from_yaml('shop1.yaml')
