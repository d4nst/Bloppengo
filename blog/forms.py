from django.forms import ModelForm
from models import Article, User


class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = ['header', 'content']
