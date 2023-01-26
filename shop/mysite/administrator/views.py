from django.shortcuts import render, redirect, get_object_or_404
from django.views import generic #継承すべきListViewをgenericモジュールに導入する
from shopping.models import Item, Purchase, PurchaseDetail #モデル、データ源を導入する
from account.models import User
from django.urls import reverse_lazy
from django.utils import timezone
from shopping.forms import SearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from . import forms
from . import models
import logging
import datetime

logger = logging.getLogger('login') # loggerを指定

def paginate_queryset(request, queryset, count):
    """Pageオブジェクトを返す。
    ページングしたい場合に利用してください。
    countは、1ページに表示する件数です。
    返却するPgaeオブジェクトは、以下のような感じで使えます。
        {% if page_obj.has_previous %}
          <a href="?page={{ page_obj.previous_page_number }}">Prev</a>
        {% endif %}
    また、page_obj.object_list で、count件数分の絞り込まれたquerysetが取得できます。
    """
    paginator = Paginator(queryset, count)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj

def login(request):
    if request.session.get('is_admin', None):
        return redirect('/administrator')
    if request.method == 'POST':
        print("ok")
        login_form = forms.UserForm(request.POST) #ログインForm生成
        message = '入力した内容を再度確認してください'
        if login_form.is_valid():
            admin_id = login_form.cleaned_data.get('id')
            password = login_form.cleaned_data.get('password')
            try:
                admin = models.Admin.objects.get(admin_id=admin_id)
            except :
                message = 'この管理者ユーザが存在しません'
                return render(request, 'administrator/login.html', locals())
            if admin.password == password:
                request.session['is_admin'] = True #session書き込み
                logger.info('url:%s method:%s admin:%s login'% (request.path, request.method, admin.admin_id)) #log
                return redirect('/administrator')
            else:
                message = 'パスワードが正しくありません。'
                return render(request, 'administrator/login.html', locals())
        else:
            return render(request, 'administrator/login.html', locals())
    login_form = forms.UserForm()
    return render(request, 'administrator/login.html', locals())

def logout(request):
    if not request.session.get('is_admin', None):
        return redirect("/administrator/login/")
    request.session.flush()
    return redirect("/administrator/login/")

def register_admin(request):
    if request.session.get('is_admin', None): #ログインしていない状態確認
        return redirect('/administrator/')

    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = "入力した内容を再度確認してください"
        if register_form.is_valid(): #form検査
            admin_id = register_form.cleaned_data.get('id')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            name = register_form.cleaned_data.get('name')

            if password1 != password2:
                message = '二回入力されたパスワードが一致しません。'
                return render(request, 'administrator/registerAdmin.html', locals())
            else:
                same_id_user = models.Admin.objects.filter(admin_id=admin_id)
                if same_id_user:
                    message = 'この管理者IDが登録済です。'
                    return render(request, 'administrator/registerAdmin.html', locals())
                new_admin = models.Admin()
                new_admin.admin_id = admin_id
                new_admin.password = password1
                new_admin.name = name
                new_admin.save()
                return render(request, 'administrator/registerAdminSuccess.html', locals())
        else:
            return render(request, 'administrator/registerAdmin.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'administrator/registerAdmin.html', locals())

class Index(generic.View):
    template_name = 'administrator/main.html'

    def get(self, request):
        if not request.session.get('is_admin', None):
            return redirect("/administrator/login/")
        search_form = SearchForm() #検索Form生成
        user_search_form = forms.UserSearchForm()
        purchase_search_form = forms.PurchaseSearchForm()
        context = {
            'search_form': search_form,
            'user_search_form': user_search_form,
            'purchase_search_form': purchase_search_form,
        }
        return render(request, self.template_name, context=context)

class ItemList(generic.ListView): #ListViewを定義し,generic.listviewを継承する
    model = Item #モデルを指定する
    context_object_name = 'item_list' #レンダリングテンプレートのcontext objectを定義し、デフォルトの名前はmodel_name_listであり、context_object_nameで上書きすることができる
    template_name = 'administrator/itemSearch.html' #指定しない場合は、デフォルトでmodel_name_list.htmlとなる
    # paginate_by = 5 #ページング
    def get(self, request):
        if not request.session.get('is_admin', None):
            return redirect("login/")
        queryset = Item.objects.all().order_by('-item_id')
        keyword = request.GET.get('keyword')
        category = int(request.GET.get('category'))
        if category == 0: #すべてのカテゴリ
            queryset = Item.objects.filter(name__contains=keyword) #filterフィルタの結果条件に一致するオブジェクトが複数ある
        else:
            queryset = Item.objects.filter(category_id=category,name__contains=keyword)
        page_obj = paginate_queryset(request, queryset, 3)
        context = {
            # 'item_list': queryset,
            'keyword': keyword,
            'category': category,
            'item_list': page_obj.object_list,
            'page_obj': page_obj,
        }
        return render(request, self.template_name, context=context)

class ItemCreate(generic.CreateView):
    model = Item #モデルを指定する
    template_name = 'administrator/item_form.html'    # 表オブジェクトのテンプレートページを追加する
    # success_url = reverse_lazy('administrator:item_list')
    success_url = '/administrator'
    fields = ['item_id', 'name', 'manufacturer', 'color', 'price', 'stock', 'recommended', 'category']
    def add(request):
        form = Item(request.POST or None)
        if form.is_valid():
            instance.save()
        context = {
            'form': form,
        }
        #有効なコミットがない場合は、元のページに残る
        return render(request, 'administrator/item_list.html',  context)

class ItemUpdate(generic.UpdateView):
    model = Item
    template_name = 'administrator/item_form.html'
    # success_url = reverse_lazy('administrator:')
    success_url = '/administrator'
    fields = ['name', 'manufacturer', 'color', 'price', 'stock', 'recommended', 'category']

class ItemDelete(generic.DeleteView):
    model = Item
    template_name = 'administrator/item_confirm_delete.html'
    success_url = reverse_lazy('administrator:')
    success_url = '/administrator'

class ItemDetail(generic.DetailView):
    model = Item   #modelをItemと指定し,Djangoに取得したいモデルがItemであることを伝えた。
    context_object_name = 'item_detail'   #取得したモデルリストのデータが保持する変数名を指定する。この変数はテンプレートに渡される。
    template_name = 'administrator/item_detail.html'
    def get_context_data(self, **kwargs):
        context = super(ItemDetail, self).get_context_data(**kwargs)
        context['now'] = timezone.now() #contextに追加
        return context

class UserList(generic.ListView):
    model = User
    context_object_name = 'user_list'
    template_name = 'administrator/userSearch.html'
    # paginate_by = 5 #ページング
    def get(self, request):
        queryset = User.objects.all().order_by('-user_id')
        keyword = request.GET.get('keyword')
        queryset = User.objects.filter(user_id__contains=keyword)
        context = {
            'user_list': queryset,
        }
        return render(request, self.template_name, context=context)

class UserUpdate(generic.UpdateView):
    model = User
    template_name = 'administrator/user_form.html'
    success_url = reverse_lazy('administrator:index')
    fields = ['user_id', 'name', 'password','address']

class UserDelete(generic.DeleteView):
    model = User
    template_name = 'administrator/user_confirm_delete.html'
    success_url = reverse_lazy('administrator:index')

class PurchaseList(generic.ListView):
    model = Purchase
    context_object_name = 'purchase_list'
    template_name = 'administrator/purchaseSearch.html'
    # paginate_by = 5 #ページング
    def get(self, request):
        queryset = Purchase.objects.all().order_by('-purchase_id')
        # 検索対象のユーザ名取得
        keyword = request.GET.get('keyword')
        start = datetime.date(int(request.GET.get('from_y')), int(request.GET.get('from_m')), int(request.GET.get('from_d')))
        end = datetime.date(int(request.GET.get('to_y')), int(request.GET.get('to_m')), int(request.GET.get('to_d')))
        end = end + datetime.timedelta(days=1)#end日付を＋1
        queryset = Purchase.objects.filter(user__user_id__icontains=keyword,
            booked_date__range=[start, end])    #外部キーならmodel__class__icontains=
        context = {
            'purchase_list': queryset,
        }
        if queryset:
            queryset_detail = PurchaseDetail.objects.filter(purchase__user__user_id__icontains=keyword,
                purchase__booked_date__range=[start, end])
            if queryset_detail:
                context['detail_list'] = queryset_detail
        print(context)
        return render(request, self.template_name, context=context)

class PurchaseDelete(generic.DeleteView):
    model =Purchase
    template_name = 'administrator/purchase_confirm_delete.html'
    success_url = reverse_lazy('administrator:index')