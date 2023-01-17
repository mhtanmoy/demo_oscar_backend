import xlsxwriter
from apps.catalogue.models import Category
from apps.partner.models import Zone
from apps.partner.models import Partner
from oscar.apps.catalogue.models import ProductClass
# Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook('scripts/Product_Details-001.xlsx')
bold = workbook.add_format({'bold': True,'bg_color':'#00FF00','locked': True})
worksheet = workbook.add_worksheet('001')
worksheet_list = workbook.add_worksheet('List')

product_dict = {"structure":"","is_public":"","ups":"","parent":"",
        "title":"","slug":"","description":"","meta_title":"","meta_description":"",
        "product_type":"","attribute_name":"","attribute_value":"","product_options":"","recommended_products":"",
        "catagories":"","is_discountable":"","objects":"",
        "index":"","zone":"","unit":"","short_discription":"","partner":"","partner_sku":"","price":"","num_in_stock":"",
        "num_allocated":"","low_stock_threshold":"","product_image":"","image_caption":""}


col = 0
for item in list(product_dict):
    worksheet.write(0, col, item ,bold )
    col+=1


catagory_qs = Category.objects.all()
category_list = []
worksheet_list.write(0,0, 'Category')
row = 1
for item in catagory_qs:
    worksheet_list.write(row, 0, item.name )
    category_list.append(item.name)
    row += 1
print(category_list)

zone_qs = Zone.objects.all()
zone_list=[]
worksheet_list.write(0,1, 'Zone')
row = 1
for item in zone_qs:
    worksheet_list.write(row, 1, item.title )
    zone_list.append(item.title)
    row += 1
print(zone_list)

partner_qs = Partner.objects.all()
partner_list=[]
worksheet_list.write(0,2, 'Partner')
row = 1
for item in partner_qs:
    worksheet_list.write(row, 2, item.id )
    partner_list.append(item.id)
    row += 1
print(partner_list)

productClass_qs = ProductClass.objects.all()
productClass_list=[]
worksheet_list.write(0,3, 'ProductClass')
row = 1
for item in productClass_qs:
    worksheet_list.write(row, 3, item.name )
    productClass_list.append(item.name)
    row += 1
print(productClass_list)

structure_list = ['Stand-alone product','Parent product','Child product']
worksheet_list.protect()

'''
Adding Validation to cells:
'''
worksheet.data_validation('A2:A50', {'validate': 'list',
                                  'source': structure_list})

worksheet.data_validation('B2:B50', {'validate': 'list',
                                  'source': ['True','False']})

worksheet.data_validation('J2:J50', {'validate': 'list',
                                  'source': productClass_list})

worksheet.data_validation('O2:O50', {'validate': 'list',
                                  'source': category_list})

worksheet.data_validation('P2:P50', {'validate': 'list',
                                  'source': ['True','False']})

worksheet.data_validation('S2:S50', {'validate': 'list',
                                  'source': zone_list})

worksheet.data_validation('V2:V50', {'validate': 'list',
                                  'source': partner_list})                                 


workbook.close()



#Python manage.py runscript generate_xl
