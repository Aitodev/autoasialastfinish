from main.models import Category, Subcategory, Subcategory1, Brand, Automodel, Manufacturer, Product
from uploader.forms import CsvUploadForm
from uploader.models import UploadModel
from django.shortcuts import redirect
from django.contrib import admin
from django.urls import path
from decimal import Decimal
import tempfile
import codecs
import xlrd
import csv


class CsvUploadAdmin(admin.ModelAdmin):
    change_list_template = "uploader.html"

    def get_urls(self):
        urls = super().get_urls()
        additional_urls = [
            path("upload-csv/", self.upload_csv),
        ]
        return additional_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra = extra_context or {}
        extra["csv_upload_form"] = CsvUploadForm()
        return super(CsvUploadAdmin, self).changelist_view(request, extra_context=extra)

    def upload_csv(self, request):
        if request.method == "POST":
            form = CsvUploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data['csv_file']
                temp = tempfile.NamedTemporaryFile()
                temp.write(file.read())
                if (str(file).split('.')[-1] == 'xls') or (str(file).split('.')[-1] == 'xlsx'):
                    try:
                        with xlrd.open_workbook(temp.name) as wb:
                            sh = wb.sheet_by_index(0)
                            keys = {}
                            for i in range(len(sh.row(0))):
                                if str(sh.row(0)[i].value).strip().lower() not in keys:
                                    keys[str(sh.row(0)[i].value).strip().lower()] = i
                            for i in range(1, sh.nrows):
                                if 'сategory' in keys and sh.row(i)[keys['сategory']].value:
                                    subcategory = None
                                    subcategory1 = None
                                    brand = None
                                    automodels = []
                                    automodel = None
                                    manufacturer = None
                                    category_str = str(sh.row(i)[keys['сategory']].value).strip()
                                    if Category.objects.filter(name=category_str).exists():
                                        category = Category.objects.filter(name=category_str).first()
                                    else:
                                        category = Category.objects.create(name=category_str)
                                    if 'subcategory1' in keys and sh.row(i)[keys['subcategory1']].value and category:
                                        subcategory_str = str(sh.row(i)[keys['subcategory1']].value).strip()
                                        if Subcategory.objects.filter(name=subcategory_str).exists():
                                            subcategory = Subcategory.objects.filter(name=subcategory_str).first()
                                        else:
                                            subcategory = Subcategory.objects.create(name=subcategory_str, category=category)
                                    if 'subcategory2' in keys and sh.row(i)[keys['subcategory2']].value and Subcategory:
                                        subcategory1_str = str(sh.row(i)[keys['subcategory2']].value).strip()
                                        if Subcategory1.objects.filter(name=subcategory1_str).exists():
                                            subcategory1 = Subcategory1.objects.filter(name=subcategory1_str).first()
                                        else:
                                            subcategory1 = Subcategory1.objects.create(name=subcategory1_str, subcategory=subcategory)
                                    if 'autobrand' in keys and sh.row(i)[keys['autobrand']].value:
                                        brand_str = str(sh.row(i)[keys['autobrand']].value).strip()
                                        if Brand.objects.filter(name=brand_str).exists():
                                            brand = Brand.objects.filter(name=brand_str).first()
                                        else:
                                            brand = Brand.objects.create(name=brand_str)
                                    automodels_str = [model_str for model_str in keys if 'automodel' in model_str]
                                    for model_str in automodels_str:
                                        if sh.row(i)[keys[model_str]].value and brand:
                                            automodel_str = str(sh.row(i)[keys[model_str]].value).strip()
                                            if Automodel.objects.filter(name=automodel_str).exists():
                                                automodel = Automodel.objects.filter(name=automodel_str).first()
                                            else:
                                                automodel = Automodel.objects.create(name=automodel_str, brand=brand)
                                            automodels.append(automodel)
                                    if 'manufacturer' in keys and sh.row(i)[keys['manufacturer']].value:
                                        manufacturer_str = str(sh.row(i)[keys['manufacturer']].value).strip()
                                        if Manufacturer.objects.filter(name=manufacturer_str).exists():
                                            manufacturer = Manufacturer.objects.filter(name=manufacturer_str).first()
                                        else:
                                            manufacturer = Manufacturer.objects.create(name=manufacturer_str)
                                    code = str(sh.row(i)[keys['productcode']].value).strip() if 'productcode' in keys else None
                                    name = str(sh.row(i)[keys['productname']].value).strip() if 'productname' in keys else None
                                    description = str(sh.row(i)[keys['shortdescription']].value).strip() if 'shortdescription' in keys else None
                                    price = str(sh.row(i)[keys['price']].value).strip() if 'price' in keys else None
                                    if name:
                                        if automodels:
                                            for automodel in automodels:
                                                Product.objects.create(name=name, description=description, product_code=code, category=category, price=price, manufacturer=manufacturer,
                                                                       subcategory=subcategory, subcategory1=subcategory1, brand=brand, automodel=automodel)
                                        else:
                                            Product.objects.create(name=name, description=description, product_code=code, category=category, price=price, manufacturer=manufacturer,
                                                                   subcategory=subcategory, subcategory1=subcategory1, brand=brand, automodel=automodel)
                                        # LOOKS LIKE THE EXCEL FILE IS WRONG !!!
                                        automodels_2 = []
                                        if sh.row(i)[11].value:
                                            if Brand.objects.filter(name=sh.row(i)[11].value).exists():
                                                brand = Brand.objects.filter(name=sh.row(i)[11].value).first()
                                            else:
                                                brand = Brand.objects.create(name=sh.row(i)[11].value)
                                        if sh.row(i)[12].value:
                                            if Automodel.objects.filter(name=sh.row(i)[12].value).exists():
                                                automodel = Automodel.objects.filter(name=sh.row(i)[12].value).first()
                                            else:
                                                automodel = Automodel.objects.create(name=sh.row(i)[12].value, brand=brand)
                                            automodels_2.append(automodel)
                                        if sh.row(i)[13].value:
                                            if Automodel.objects.filter(name=sh.row(i)[13].value).exists():
                                                automodel = Automodel.objects.filter(name=sh.row(i)[13].value).first()
                                            else:
                                                automodel = Automodel.objects.create(name=sh.row(i)[13].value, brand=brand)
                                            automodels_2.append(automodel)
                                        if sh.row(i)[14].value:
                                            if Automodel.objects.filter(name=sh.row(i)[14].value).exists():
                                                automodel = Automodel.objects.filter(name=sh.row(i)[14].value).first()
                                            else:
                                                automodel = Automodel.objects.create(name=sh.row(i)[14].value, brand=brand)
                                            automodels_2.append(automodel)
                                        if sh.row(i)[15].value:
                                            if Manufacturer.objects.filter(name=sh.row(i)[15].value).exists():
                                                manufacturer = Manufacturer.objects.filter(name=sh.row(i)[15].value).first()
                                            else:
                                                manufacturer = Manufacturer.objects.create(name=sh.row(i)[15].value)
                                        for automodel in automodels_2:
                                            Product.objects.create(name=name, description=description, product_code=code, price=price,
                                                                   manufacturer=manufacturer, subcategory=subcategory, category=category,
                                                                   brand=brand, automodel=automodel, subcategory1=subcategory1)
                    except Exception as e:
                        raise e
                elif str(file).split('.')[-1] == 'csv':
                    data = csv.DictReader(codecs.iterdecode(file, 'utf-8'))
                    for row in data:
                        if row['Сategory']:
                            subcategory = None
                            subcategory1 = None
                            brand = None
                            automodel = None
                            automodels = []
                            manufacturer = None
                            if Category.objects.filter(name=str(row['Сategory']).strip()).exists():
                                category = Category.objects.filter(name=str(row['Сategory']).strip()).first()
                            else:
                                category = Category.objects.create(name=str(row['Сategory']).strip())
                            if row['Subcategory1']:
                                if Subcategory.objects.filter(name=str(row['Subcategory1']).strip()).exists():
                                    subcategory = Subcategory.objects.filter(name=str(row['Subcategory1']).strip()).first()
                                else:
                                    subcategory = Subcategory.objects.create(name=str(row['Subcategory1']).strip(), category=category)
                            if row['Subcategory2']:
                                if Subcategory1.objects.filter(name=str(row['Subcategory2']).strip()).exists():
                                    subcategory1 = Subcategory1.objects.filter(name=str(row['Subcategory2']).strip()).first()
                                else:
                                    subcategory1 = Subcategory1.objects.create(name=str(row['Subcategory2']).strip(), subcategory=subcategory)
                            if row['Autobrand']:
                                if Brand.objects.filter(name=str(row['Aufobrand']).strip()).exists():
                                    brand = Brand.objects.filter(name=str(row['Aufobrand']).strip()).first()
                                else:
                                    brand = Brand.objects.create(name=str(row['Aufobrand']).strip())
                            if row['Automodel1']:
                                if Automodel.objects.filter(name=str(row['Automodel1']).strip()).exists():
                                    automodel = Automodel.objects.filter(name=str(row['Automodel1']).strip()).first()
                                else:
                                    automodel = Automodel.objects.create(name=str(row['Automodel1']).strip(), brand=brand)
                                automodels.append(automodel)
                            if row['Automodel2']:
                                if Automodel.objects.filter(name=str(row['Automodel2']).strip()).exists():
                                    automodel1 = Automodel.objects.filter(name=str(row['Automodel2']).strip()).first()
                                else:
                                    automodel1 = Automodel.objects.create(name=str(row['Automodel2']).strip(), brand=brand)
                                automodels.append(automodel1)
                            if row['Automodel3']:
                                if Automodel.objects.filter(name=str(row['Automodel3']).strip()).exists():
                                    automodel2 = Automodel.objects.filter(name=str(row['Automodel3']).strip()).first()
                                else:
                                    automodel2 = Automodel.objects.create(name=str(row['Automodel3']).strip(), brand=brand)
                                automodels.append(automodel2)
                            if row['manufacturer']:
                                if Manufacturer.objects.filter(name=str(row['manufacturer']).strip()).exists():
                                    manufacturer = Manufacturer.objects.filter(name=str(row['manufacturer']).strip()).first()
                                else:
                                    manufacturer = Manufacturer.objects.create(name=str(row['manufacturer']).strip())
                            code = str(row['Productcode']).strip()
                            name = str(row['Productname']).strip()
                            description = str(row['Shortdescription']).strip()
                            price = Decimal(row['Price'].replace(',', '').strip())
                            if name:
                                if automodels:
                                    for automodel in automodels:
                                        Product.objects.create(name=name, description=description, product_code=code, category=category, price=price, automodel=automodel,
                                                               manufacturer=manufacturer, subcategory=subcategory, subcategory1=subcategory1, brand=brand)
                                else:
                                    Product.objects.create(name=name, description=description, product_code=code, category=category, price=price, automodel=automodel,
                                                           manufacturer=manufacturer, subcategory=subcategory, subcategory1=subcategory1, brand=brand)
            return redirect("..")


admin.site.register(UploadModel, CsvUploadAdmin)

# 0 'Сategory', 1 'Subcategory1', 2 'Subcategory2',
# 3 'Productcode', 4 'Productname', 5 'Shortdescription',
# 6 'Aufobrand', 7 'Automodel1', 8 'Automodel2',
# 9 'Automodel3', 10 'manufacturer', 11'Aufobrand',
# 12 'Automodel1', 13 'Automodel2', 14 'Automodel3',
# 15 'manufacturer', 16 'Price'
# # LOOKS LIKE THE EXCEL FILE IS WRONG !!!
# automodel = None
# automodel1 = None
# automodel2 = None
# manufacturer = None
# if sh.row(row)[11].value:
#     if Brand.objects.filter(name=sh.row(row)[11].value).exists():
#         brand = Brand.objects.filter(name=sh.row(row)[11].value).first()
#     else:
#         brand = Brand.objects.create(name=sh.row(row)[11].value)
# if sh.row(row)[12].value:
#     if Automodel.objects.filter(name=sh.row(row)[12].value).exists():
#         automodel = Automodel.objects.filter(name=sh.row(row)[12].value).first()
#     else:
#         automodel = Automodel.objects.create(name=sh.row(row)[12].value, brand=brand)
# if sh.row(row)[13].value:
#     if Automodel1.objects.filter(name=sh.row(row)[13].value).exists():
#         automodel1 = Automodel1.objects.filter(name=sh.row(row)[13].value).first()
#     else:
#         automodel1 = Automodel1.objects.create(name=sh.row(row)[13].value, automodel=automodel)
# if sh.row(row)[14].value:
#     if Automodel2.objects.filter(name=sh.row(row)[14].value).exists():
#         automodel2 = Automodel2.objects.filter(name=sh.row(row)[14].value).first()
#     else:
#         automodel2 = Automodel2.objects.create(name=sh.row(row)[14].value, automodel1=automodel1)
# if sh.row(row)[15].value:
#     if Manufacturer.objects.filter(name=sh.row(row)[15].value).exists():
#         manufacturer = Manufacturer.objects.filter(name=sh.row(row)[15].value).first()
#     else:
#         manufacturer = Manufacturer.objects.create(name=sh.row(row)[15].value)
# Product.objects.create(name=name, description=description, product_code=code, category=category, price=price,
#                        manufacturer=manufacturer, subcategory=subcategory, subcategory1=subcategory1,
#                        brand=brand, automodel=automodel, automodel1=automodel1, automodel2=automodel2)
# if 'automodel1' in keys and sh.row(i)[keys['automodel1']].value and brand:
#     automodel_str = str(sh.row(i)[keys['automodel1']].value).strip()
#     if Automodel.objects.filter(name=automodel_str).exists():
#         automodel = Automodel.objects.filter(name=automodel_str).first()
#     else:
#         automodel = Automodel.objects.create(name=automodel_str, brand=brand)