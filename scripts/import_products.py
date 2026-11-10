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
    
    categories_dict = {}
    for cat in data['categories']:
        category, _ = Category.objects.get_or_create(name=cat['name'])
        category.shops.add(shop)
        categories_dict[cat['id']] = category
        
    for good in data['goods']:
        category = categories_dict.get(good['category'])
        
        product, _ = Product.objects.update_or_create(
            name=good['name'],
            shop=shop,
            defaults={
                'category': category,
                'price': good['price'],
                'quantity': good.get('quantity', 0),
            }
        )
        
        for param_name, param_value in good.get('parameters', {}).items():
            ProductParameter.objects.update_or_create(
                product=product,
                name=param_name,
                defaults={'value': str(param_value)}
            )
    
    print(f"Импорт из {file_path} завершен.")

if __name__ == '__main__':
    import_from_yaml('shop1.yaml')
