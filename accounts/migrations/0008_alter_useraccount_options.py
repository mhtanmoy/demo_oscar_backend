# Generated by Django 3.2.16 on 2022-12-30 10:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_useraccount_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='useraccount',
            options={'permissions': (('custom_add_permission_useraccount', 'Custom can add permission useraccount'), ('custom_update_permission_useraccount', 'Custom can update permission useraccount'), ('custom_delete_permission_useraccount', 'Custom can delete permission useraccount'), ('custom_view_permission_useraccount', 'Custom can view permission useraccount'), ('custom_add_product', 'Custom can add product'), ('custom_update_product', 'Custom can update product'), ('custom_delete_product', 'Custom can delete product'), ('custom_view_all_product', 'Custom can view all product'), ('custom_update_product_category', 'Custom can update product category'), ('custom_delete_product_category', 'Custom can delete product category'), ('custom_add_product_sub_category', 'Custom can add product sub category'), ('custom_update_product_sub_category', 'Custom can update product sub category'), ('custom_delete_product_sub_category', 'Custom can delete product sub category'), ('custom_add_product_stock', 'Custom can add product stock'), ('custom_update_product_stock', 'Custom can update product stock'), ('custom_delete_product_stock', 'Custom can delete product stock'), ('custom_view_all_product_stock', 'Custom can view all product stock'), ('custom_view_all_order', 'Custom can view all order'), ('custom_view_all_order_item', 'Custom can view all order item'), ('custom_update_order', 'Custom can update order'), ('custom_update_order_item', 'Custom can update order item'), ('custom_view_order', 'Custom can view order'), ('custom_view_order_item', 'Custom can view order item'), ('custom_add_order_schedule', 'Custom can add order schedule'), ('custom_update_order_schedule', 'Custom can update order schedule'), ('custom_delete_order_schedule', 'Custom can delete order schedule'), ('custom_add_merchant', 'Custom can add merchant'), ('custom_update_merchant', 'Custom can update merchant'), ('custom_delete_merchant', 'Custom can delete merchant'), ('custom_block_merchant', 'Custom can block merchant'), ('custom_add_portfolio', 'Custom can add portfolio'), ('custom_update_portfolio', 'Custom can update portfolio'), ('custom_delete_portfolio', 'Custom can delete portfolio'), ('custom_add_employee', 'Custom can add employee'), ('custom_update_employee', 'Custom can update employee'), ('custom_delete_employee', 'Custom can delete employee'), ('custom_block_employee', 'Custom can block employee'), ('custom_add_partner', 'Custom can add partner'), ('custom_update_partner', 'Custom can update partner'), ('custom_delete_partner', 'Custom can delete partner'), ('custom_add_promo_code', 'Custom can add promo code'), ('custom_update_promo_code', 'Custom can update promo code'), ('custom_delete_promo_code', 'Custom can delete promo code'), ('custom_add_discount', 'Custom can add discount'), ('custom_update_discount', 'Custom can update discount'), ('custom_delete_discount', 'Custom can delete discount'), ('custom_add_customer', 'Custom can add customer'), ('custom_update_customer', 'Custom can update customer'), ('custom_delete_customer', 'Custom can delete customer'), ('custom_block_customer', 'Custom can block customer'), ('custom_add_notification', 'Custom can add notification'), ('custom_update_notification', 'Custom can update notification'), ('custom_delete_notification', 'Custom can delete notification'), ('custom_add_version', 'Custom can add version'), ('custom_update_version', 'Custom can update version'), ('custom_delete_version', 'Custom can delete version'), ('custom_delete_review', 'Custom can delete review'))},
        ),
    ]