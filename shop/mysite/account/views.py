from django.shortcuts import render
from django.shortcuts import redirect
from . import models
from . import forms
import logging

# Create your views here.

logger = logging.getLogger('login') # loggerを指定

def index(request):
    return redirect('/')

def login(request):
    if request.session.get('is_login', None):
        return redirect('/')
    if request.method == 'POST':
        login_form = forms.UserForm(request.POST) #ログインForm生成
        message = '入力した内容を再度確認してください'
        if login_form.is_valid():
            user_id = login_form.cleaned_data.get('id')
            password = login_form.cleaned_data.get('password')
            try:
                user = models.User.objects.get(user_id=user_id)
            except :
                message = 'ユーザが存在しません'
                return render(request, 'account/login.html', locals()) #この環境内で定義されている変数を辞書として取得できる
            if user.password == password:
                request.session['is_login'] = True #session書き込み
                request.session['user_id'] = user.user_id
                request.session['user_name'] = user.name
                logger.info('url:%s method:%s user:%s login'% (request.path, request.method, user.user_id)) #log
                return redirect('/')
            else:
                message = 'パスワードが正しくありません。'
                return render(request, 'account/login.html', locals())
        else:
            return render(request, 'account/login.html', locals())

    login_form = forms.UserForm()
    return render(request, 'account/login.html', locals())

def logout(request):
    if not request.session.get('is_login', None):
        return redirect("/account/login/")
    # request.session.clear()
    request.session.flush() #session削除
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/account/login/")

def register_user(request):
    if request.session.get('is_login', None): #ログインしていない状態確認
        return redirect('/')

    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = "入力した内容を再度確認してください"
        if register_form.is_valid(): #form検査
            user_id = register_form.cleaned_data.get('id')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            name = register_form.cleaned_data.get('name')
            address = register_form.cleaned_data.get('address')
            if password1 != password2:
                message = '二回入力されたパスワードが一致しません。'
                return render(request, 'account/registerUser.html', locals())
            else:
                same_id_user = models.User.objects.filter(user_id=user_id)
                if same_id_user:
                    message = 'この会員IDが登録済です。'
                    return render(request, 'account/registerUser.html', locals())
                return render(request, 'account/registerUserConfirm.html', locals())
        else:
            return render(request, 'account/registerUser.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'account/registerUser.html', locals())

def register_user_commit(request):
    if request.session.get('is_login', None):
        return redirect('/')
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        if register_form.is_valid():
            user_id = register_form.cleaned_data.get('id')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            name = register_form.cleaned_data.get('name')
            address = register_form.cleaned_data.get('address')
            new_user = models.User()
            new_user.user_id = user_id
            new_user.password = password1
            new_user.name = name
            new_user.address = address
            new_user.save()
            request.session['is_login'] = True
            request.session['user_id'] = new_user.user_id
            request.session['user_name'] = new_user.name
            return render(request, 'account/registerUserCommit.html')
        else:
            return render(request, 'account/registerUser.html', locals())
    register_form = forms.RegisterForm()
    return render(request, 'account/registerUser.html', locals())

def user_info(request):
    if not request.session.get('is_login', None):
        return redirect("/account/login/")
    user_id = request.session['user_id']
    user = models.User.objects.get(user_id=user_id)
    id = user_id
    name = user.name
    address = user.address
    register_form = forms.RegisterForm()
    return render(request, 'account/userInfo.html', locals())

def update_user(request):
    if not request.session.get('is_login', None):
        return redirect("/account/login/")
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        message = "入力した内容を再度確認してください"
        if register_form.is_valid():
            id = register_form.cleaned_data.get('id')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            name = register_form.cleaned_data.get('name')
            address = register_form.cleaned_data.get('address')
            if password1 != password2:
                message = '二回入力されたパスワードが一致しません'
                return render(request, 'account/updateUser.html', locals())
            else:
                return render(request, 'account/updateUserConfirm.html', locals())
        else:
            return render(request, 'account/updateUser.html', locals())
    user_id = request.session['user_id']
    user = models.User.objects.get(user_id=user_id)
    initial = True
    id = user_id
    name = user.name
    address = user.address
    register_form = forms.RegisterForm()
    return render(request, 'account/updateUser.html', locals())

def update_user_commit(request):
    if not request.session.get('is_login', None):
        return redirect("/account/login/")
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        if register_form.is_valid():
            id = register_form.cleaned_data.get('id')
            password1 = register_form.cleaned_data.get('password1')
            password2 = register_form.cleaned_data.get('password2')
            name = register_form.cleaned_data.get('name')
            address = register_form.cleaned_data.get('address')
            user = models.User.objects.get(user_id=id)
            user.name = name
            user.password = password1
            user.address = address
            user.save()
            request.session['user_name'] = user.name
            return render(request, 'account/updateUserCommit.html', locals())
        else:
            return render(request, 'account/updateUser.html', locals())
    return render(request, 'account/main.html')

def withdraw(request):
    if not request.session.get('is_login', None):
        return redirect("/account/login/")
    return render(request, 'account/withdrawConfirm.html')

def withdraw_commit(request):
    if not request.session.get('is_login', None):
        return redirect("/account/login/")
    user_id = request.session['user_id']
    name = request.session['user_name']
    user = models.User.objects.get(user_id=user_id)
    user.delete()
    request.session.flush()
    return render(request, 'account/withdrawCommit.html', locals())