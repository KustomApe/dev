from django.shortcuts import render
from django.shortcuts import redirect
from django.views import generic
from django.views.generic import View
from message.models import Article

class IndexView(View):
    def get(self, request, *args, **kwargs):
        queryset = Article.objects.all().order_by('-created_at')
        context = {
            'article_list' : queryset,
        }
        return render(request, 'message/board.html', context)

class ArticleCreate(View):
    def get(self, request, *args, **kwargs):
        pass
    
    def post(self,request,*args,**kwargs):
        new_article = Article()
        new_article.name = request.POST['name']
        new_article.content = request.POST['content']
        new_article.password = request.POST['password']
        new_article.created_at = request.POST['created_at']
        new_article.save()
        queryset = Article.objects.all().order_by('-created_at')

        context = {
            'article_list' : queryset
        }        
        return render(request,'message/board.html',context)