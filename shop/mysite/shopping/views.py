from django.shortcuts import render
from django.shortcuts import redirect
from account.models import User
from . import models
from . import forms
import time
from datetime import datetime

# 商品検索メイン画面
def index(request):
    search_form = forms.SearchForm() #検索Form生成
    return render(request, 'shopping/main.html', locals()) #この環境内で定義されている変数を辞書として取得できる

# 商品検索
def search(request):
    if not request.method == 'GET': #GETのみ対処
        return redirect('/shopping/')
    search_form = forms.SearchForm(request.GET)
    if search_form.is_valid():
        keyword = request.GET.get('keyword')
        category_id = int(request.GET.get('category'))
        category_name = "すべて"
        if category_id == 0: #すべてのカテゴリ
            found_item = models.Item.objects.filter(name__contains=keyword) #filterフィルタの結果条件に一致するオブジェクトが複数ある
        else:
            category_name = models.Category.objects.get(category_id=category_id)#カテゴリ選択時
            found_item = models.Item.objects.filter(category_id=category_id,name__contains=keyword)
        if not keyword:
                keyword= 'なし'
        if found_item:
            form =[]
            for i in found_item:
                item = {'item_id':i.item_id, 'name':i.name, 'color':i.color, 'price':i.price, 'manufacturer':i.manufacturer, 'recommended':i.recommended}
                form.append(item)
            return render(request, 'shopping/searchResult.html',{'form':form, 'keyword':keyword, 'category_name':category_name}) #form変数を辞書として取得できる
        else:
            message = '見つかりませんでした'
            return render(request, 'shopping/searchResult.html', {'message':message, 'keyword':keyword, 'category_name':category_name})

# 商品詳細表示
def item_detail(request,item_id):
    try:
        found_item = models.Item.objects.get(item_id=item_id) #getフィルタの結果条件に一致するオブジェクトが一つだけ
        form =[]
        if found_item:
            # ログインしたユーザーの選択した商品IDがcartに存在する場合は注文数分、在庫を減らす
            if request.session.get('is_login', None): #既にログインしている場合
                user_id = request.session['user_id']
                item_in_cart = models.ItemsInCart.objects.filter(item_id=item_id, user_id=user_id)
                if item_in_cart:
                    found_item.stock -= item_in_cart[0].amount
                    if found_item.stock < 0:
                        found_item.stock = 0
            # 商品詳細情報
            item_detail = {'item_id':item_id, 'name':found_item.name, 'color':found_item.color,
                'price':found_item.price, 'manufacturer':found_item.manufacturer, 'stock':found_item.stock}
            form.append(item_detail)
        return render(request, 'shopping/itemDetail.html',{'form':form})
    except:
        return redirect('/shopping/')
    return redirect('/shopping/')

# cartに商品追加
def add_to_cart(request):
    if not request.session.get('is_login', None): #ログイン状態確認
        return redirect("/account/login/")
    if not request.method == 'POST': #Not POST通信
        return redirect('/shopping/')
    user_id = request.session['user_id']
    item_id = int(request.POST.get('itemId'))
    amount = int(request.POST.get('amount'))
    # ログインユーザが選択したitemがitem_in_cartにあればマージ、なければ新しく追加
    item_in_cart = models.ItemsInCart.objects.filter(item_id=item_id, user_id=user_id)
    if item_in_cart:# マージ
        item_in_cart[0].amount += amount
        item_in_cart[0].save()
    else:# 新しく追加
        user = User.objects.get(user_id=user_id) #from account.models import Userにより別アプリのモデルが使える
        item = models.Item.objects.get(item_id=item_id)
        new_cart = models.ItemsInCart() #新しいItemsInCart作成
        new_cart.user = user
        new_cart.item = item
        new_cart.amount = amount
        new_cart.save() #DB書き込み
    return redirect('/shopping/cart/')

# cart表示
def cart(request):
    if not request.session.get('is_login', None):
        return redirect("/account/login/")
    user_id = request.session['user_id']
    cart_item = models.ItemsInCart.objects.filter(user_id=user_id)
    if cart_item:
        form =[]
        total_price = 0
        for i in cart_item:
            cart = {'id':i.id, 'item_id':i.item.item_id, 'name':i.item.name, 'color':i.item.color,
            'price':i.item.price, 'manufacturer':i.item.manufacturer, 'amount':i.amount, 'stock':i.item.stock}
            total_price = total_price + i.item.price*i.amount
            form.append(cart)
    else:
        message = '商品がありません'
        return render(request, 'shopping/cart.html', {'message':message})
    return render(request, 'shopping/cart.html', locals())

# cart数量変更
def amount_in_cart(request):
    if not request.session.get('is_login', None):
        return redirect("/account/login/")
    if request.method == 'POST': #POST通信
        user_id = request.session['user_id'] #session
        id = int(request.POST.get('id'))
        amount = int(request.POST.get('amount'))
        item_in_cart = models.ItemsInCart.objects.get(id=id)
        if item_in_cart:
            item_in_cart.amount = amount
            item_in_cart.save()
    return redirect('/shopping/cart/')

# cart から削除する商品選択
def remove_from_cart(request,id):
    if not request.session.get('is_login', None):
        return redirect("/account/login/")
    item_in_cart = models.ItemsInCart.objects.get(id=id)
    if item_in_cart:
        form =[]
        cart = {'id':id, 'name':item_in_cart.item.name,
        'price':item_in_cart.item.price, 'manufacturer':item_in_cart.item.manufacturer,
        'amount':item_in_cart.amount}
        form.append(cart)
        return render(request, 'shopping/removeFromCartConfirm.html', locals())
    return redirect('/shopping/cart/')

# cart から商品削除実行
def remove_from_cart_commit(request):
    if not request.session.get('is_login', None):
        return redirect("/account/login/")
    if request.method == 'POST':
        user_id = request.session['user_id']
        id = int(request.POST.get('id'))
        item_in_cart = models.ItemsInCart.objects.get(id=id)
        if item_in_cart:
            form =[]
            cart = {'id':item_in_cart.id, 'name':item_in_cart.item.name,
            'price':item_in_cart.item.price, 'manufacturer':item_in_cart.item.manufacturer,
            'amount':item_in_cart.amount}
            form.append(cart)
            item_in_cart.delete() #削除をDB書き込み
            return render(request, 'shopping/removeFromCartCommit.html', locals())
    return redirect('/shopping/cart/')

# 購入する 購入確認画面へ
def purchase(request):
    if not request.session.get('is_login', None):
        return redirect("/account/login/")
    user_id = request.session['user_id']
    cart_item = models.ItemsInCart.objects.filter(user_id=user_id)
    if cart_item:
        form =[]
        total_price = 0
        for i in cart_item:
            cart = {'item_id':i.item.item_id, 'name':i.item.name, 'color':i.item.color, 'price':i.item.price,
            'manufacturer':i.item.manufacturer, 'amount':i.amount}
            total_price = total_price + i.item.price*i.amount #合計金額計算
            form.append(cart)
    return render(request, 'shopping/purchaseConfirm.html', locals())

# 購入確定 購入完了画面へ
def purchase_commit(request):
    if not request.session.get('is_login', None):
        return redirect("/account/login/")
    if request.method == 'POST':
        user_id = request.session['user_id']
        destination = request.POST.get('destination')
        address = request.POST.get('address')
        cart_item = models.ItemsInCart.objects.filter(user_id=user_id)
        if cart_item:
            count = models.Purchase.objects.count() #注文ID自動生成
            user = User.objects.get(user_id=user_id)
            if destination == 'registered': #配送先が自宅かを判別
                address = user.address
            new_purchase = models.Purchase() #新しい注文作成
            new_purchase.purchase_id = count + 1 #Purchase_id自動生成
            new_purchase.user = user
            new_purchase.destination = address
            # print(datetime.now)
            new_purchase.booked_date = datetime.now()
            new_purchase.save() #DB書き込み
            form =[]
            total_price = 0
            for i in cart_item: #複数種類商品を注文
                cart = {'item_id':i.item.item_id, 'name':i.item.name, 'color':i.item.color,
                'price':i.item.price, 'manufacturer':i.item.manufacturer, 'amount':i.amount}
                total_price = total_price + i.item.price*i.amount
                form.append(cart)
                new_purchase_detail = models.PurchaseDetail()
                count2 = models.PurchaseDetail.objects.count() #注文詳細ID自動生成
                new_purchase_detail.purchase_detail_id = count2 + 1 #新しい注文詳細
                new_purchase_detail.purchase = new_purchase
                new_purchase_detail.item = i.item
                new_purchase_detail.amount = i.amount
                new_purchase_detail.save()
                # 注文商品の在庫数を注文数「i.amount」分減らす
                purchase_item = models.Item.objects.get(item_id=i.item.item_id)
                purchase_item.stock = purchase_item.stock - i.amount
                purchase_item.save()
                i.delete() #ショッピングカートから商品を削除
            return render(request, 'shopping/purchaseCommit.html', locals())
    return redirect('/shopping/cart/')

# 購入履歴表示
def purchase_history(request):
    if not request.session.get('is_login', None):
        return redirect("/account/login/")
    user_id = request.session['user_id']
    found_purchase = models.Purchase.objects.filter(user_id=user_id)
    if found_purchase:
        form_purchase =[]
        for i in found_purchase:
            if not i.cancel: #キャンセルしたかを判別
                found_detail = models.PurchaseDetail.objects.filter(purchase_id=i.purchase_id)
                form_detail =[]
                for j in found_detail:
                    detail = {'name':j.item.name, 'color':j.item.color, 'price':j.item.price, 'manufacturer':j.item.manufacturer, 'amount':j.amount}
                    form_detail.append(detail)
                purchase = {'purchase_id':i.purchase_id, 'booked_date':i.booked_date.strftime('%Y-%m-%d %H:%M'), 'destination':i.destination, 'detail':form_detail}
                form_purchase.append(purchase)
        return render(request, 'shopping/purchaseHistory.html', locals())
    else:
        message = '見つかりませんでした'
        return render(request, 'shopping/purchaseHistory.html', {'message':message})
    return redirect('/shopping/')

# 購入キャンセル キャンセル確認画面へ
def purchase_cancel(request,purchase_id):
    if not request.session.get('is_login', None):
        return redirect("/account/login/")
    found_purchase = models.Purchase.objects.get(purchase_id=purchase_id)
    if found_purchase:
        form_purchase =[]
        i = found_purchase
        found_detail = models.PurchaseDetail.objects.filter(purchase_id=i.purchase_id)
        form_detail =[]
        for j in found_detail:
            detail = {'name':j.item.name, 'color':j.item.color, 'price':j.item.price, 'manufacturer':j.item.manufacturer, 'amount':j.amount}
            form_detail.append(detail)
        purchase = {'purchase_id':i.purchase_id, 'booked_date':i.booked_date.strftime('%Y-%m-%d %H:%M'), 'destination':i.destination, 'cancel':i.cancel, 'detail':form_detail}
        form_purchase.append(purchase)
        return render(request, 'shopping/purchaseCancelConfirm.html', locals())

# 購入キャンセル確定
def purchase_cancel_commit(request):
    if not request.session.get('is_login', None):
        return redirect("/account/login/")
    if request.method == 'POST':
        purchase_id = request.POST.get('purchaseId')
        found_purchase = models.Purchase.objects.get(purchase_id=purchase_id)
        if found_purchase:
            found_purchase.cancel = True
            found_purchase.save()
            form_purchase =[]
            i = found_purchase
            found_detail = models.PurchaseDetail.objects.filter(purchase_id=i.purchase_id)
            form_detail =[]
            for j in found_detail:
                detail = {'name':j.item.name, 'color':j.item.color, 'price':j.item.price, 'manufacturer':j.item.manufacturer, 'amount':j.amount}
                form_detail.append(detail)
            purchase = {'purchase_id':i.purchase_id, 'booked_date':i.booked_date.strftime('%Y-%m-%d %H:%M'), 'destination':i.destination, 'detail':form_detail}
            form_purchase.append(purchase)
            return render(request, 'shopping/purchaseCancelCommit.html', locals())
