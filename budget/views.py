from django.shortcuts import render,redirect
from django.views.generic import View
from budget.models import Transaction
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.utils import timezone
from django.db.models import Sum



    # fields="__all__"
    # exclude=(" ",)
    # fields=["feild1","feild2"]

class TransactionForm(forms.ModelForm):
    class Meta:
        model=Transaction
        exclude=("created_date","user_object")

class RegistrationForm(forms.ModelForm):
    class Meta:
        model=User
        fields=["username","email","password"]


# view for listing all transactions
# url:localhost:8000/transactions/all
# method: get

class TransactionListView(View):
    def get(self,request,*args,**kwargs):
        qs=Transaction.objects.filter(user_object=request.user)
        curr_month=timezone.now().month
        curr_year=timezone.now().year
        # print(curr_month,curr_year)
        data=Transaction.objects.filter(
            created_date__month=curr_month,
            created_date__year=curr_year,
            user_object=request.user
        ).values("type").annotate(type_sum=Sum("amount"))
        print(data)
        

        cat_qs=Transaction.objects.filter(
            created_date__month=curr_month,
            created_date__year=curr_year,
            user_object=request.user
        ).values("category").annotate(category_sum=Sum("amount"))
        print(cat_qs)

        return render(request,"transaction_list.html",{"data":qs,"type_total":data,"cat_total":cat_qs})
    

        # expense_total=Transaction.objects.filter(
        #     user_object=request.user,
        #     type="expense",
        #     created_date__month=curr_month,
        #     created_date__year=curr_year
        # ).aggregate(Sum("amount"))
        # print(expense_total)
        

        # income_total=Transaction.objects.filter(
        #     user_object=request.user,
        #     type="income",
        #     created_date__month=curr_month,
        #     created_date__year=curr_year
        # ).aggregate(Sum("amount"))
        # print(income_total)
    
    

# view for creating new transaction
# url:localhost:8000/transactions/add/
# methods:get,post

class TransactionCreateView(View):
    def get(self,request,*args,**kwargs):
        form=TransactionForm()
        return render(request,"transaction_add.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=TransactionForm(request.POST)
        if form.is_valid():
            # form.save()
            data=form.cleaned_data
            Transaction.objects.create(**data,user_object=request.user)
            return redirect("transaction-list")
        else:
            return render(request,"transaction_add.html",{"form":form})    

# transactio detail view
# url : localhost:8000/transactions/{id}/
# method: get
class TransactionDetailView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        qs=Transaction.objects.get(id=id)
        return render(request,"transaction_detail.html",{"data":qs})


#transaction detail view
#url:localhost:8000/transactions/{id}/remove/
#methods: get
class TransactionDeleteView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        Transaction.objects.filter(id=id).delete()
        return redirect("transaction-list")

#transaction update view
# localhost:8000/{id}/change/
# methods: get , post
class TransactionUpdateView(View):
    def get(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        Transaction_object=Transaction.objects.get(id=id)
        form=TransactionForm(instance=Transaction_object)
        return render(request,"transaction_edit.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        id=kwargs.get("pk")
        Transaction_object=Transaction.objects.get(id=id)
        form=TransactionForm(request.POST,instance=Transaction_object)
        if form.is_valid():
            form.save()
            return redirect("transaction-list")
        else:
            return render(request,"transaction_edit.html",{"form":form})


#registration view
#localhost:8000/signup
#method: get , post
        
class SignupView(View):
    def get(self,request,*args,**kwargs):
        form=RegistrationForm()
        return render(request,"register.html",{"form":form})
    
    def post(self,request,*args,**kwargs):
        form=RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(**form.cleaned_data)
            print("account created")
            return redirect("signin")
        else:
            print("failed to create")
            return render(request,"register.html",{"form":form})

class LoginForm(forms.Form):
    username=forms.CharField()
    password=forms.CharField()

#sign in view
#url : localhost:8000/signin/
#method :get,post
    
class SignInView(View):
    def get(self,request,*args,**kwargs):
        form=LoginForm()
        return render(request,"login.html",{"form":form})
    def post(self,request,*args,**kwargs):
        form=LoginForm(request.POST)
        if form.is_valid():
            u_name=form.cleaned_data.get("username")
            pwd=form.cleaned_data.get("password")
            user_object=authenticate(request,username=u_name,password=pwd)
            if user_object:
                #start session
                login(request,user_object)
                #request.user =>anonymous user (user has no session)
                return redirect("transaction-list")

        return render(request,"login.html",{"form":form})
    
class SignOutView(View):
    def get(self,request,*args,**kwargs):
        logout(request)
        return redirect("signin")

