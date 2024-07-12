from django.db import models

class Article(models.Model):
	# 記事モデル
    class Meta:
    	# テーブル名定義
    	db_table = 'articles'

    # テーブルフィールド定義
    name = models.CharField(verbose_name='投稿者名', max_length=255)
    password = models.CharField(verbose_name='投稿者パスワード', max_length=255)
    content = models.TextField(verbose_name='投稿内容', max_length=1000)
    votes = models.IntegerField(verbose_name='投票数', default=0)
    created_at = models.DateTimeField(verbose_name='投稿日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', null=True, blank=True)
    
    def __str__(self):
        return self.content

class Comment(models.Model):
	# 記事モデル
    class Meta:
    	# テーブル名定義
    	db_table = 'comments'

    # テーブルフィールド定義
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    name = models.CharField(verbose_name='コメント者名', max_length=255)
    password = models.CharField(verbose_name='コメント者パスワード', max_length=255)
    content = models.TextField(verbose_name='コメント内容', max_length=1000)
    created_at = models.DateTimeField(verbose_name='コメント記入日時', auto_now_add=True)
    
    def __str__(self):
        return self.content
