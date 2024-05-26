from django import forms
from store.models import Product
from category.models import Category
from orders.models import Order
class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('product_name','description','price','images','stock','is_available','category','slug')
        widgets = {
            'is_available': forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')]),
        }

        def __init__(self,*args,**kwargs):
            super(ProductUpdateForm,self).__init__(*args,**kwargs)
            for field in self.fields:
                self.fields[field].widget.attrs['class']='form-control'

class CategoryUpdateForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"

    def __init__(self,*args,**kwargs):
        super(CategoryUpdateForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'

class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']

    def __init__(self,*args,**kwargs):
        super(OrderStatusUpdateForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
            