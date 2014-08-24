from django.shortcuts import render_to_response, RequestContext, redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django_ajax.decorators import ajax
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from permission_backend_nonrel.models import UserPermissionList
from forms import ArticleForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from models import Article, SavedArticle, FavouriteArticle, User
from permission_backend_nonrel import utils
from django.contrib.auth import login, logout
from django.contrib.sites.models import get_current_site
import settings


def signup(request):

    if request.method == 'POST':
        # if POST save the article
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                group = Group.objects.get(name='Reader')
                utils.add_user_to_group(user, group)
                return render_to_response('signup_sucess.html', context_instance=RequestContext(request))
            except:
                pass
    else:
        # if GET create user form
        form = UserCreationForm()

    data = {
        'form': form,
        'admin': user_in_group(request.user, 'Admin'),
        'blogger': user_in_group(request.user, 'Blogger'),
    }
    return render_to_response('signup.html', data, context_instance=RequestContext(request))


def login_view(request):

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # Okay, security check complete. Log the user in.
            login(request, form.get_user())

            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = AuthenticationForm()


    data = {
        'form': form,
    }

    return render_to_response('login.html', data, context_instance=RequestContext(request))


def admin(request):
    admin = user_in_group(request.user, 'Admin')
    if admin:
        user_list = []
        users_zipped = []
        if request.method == 'POST' and 'search' in request.POST:
            try:
                user = User.objects.get(username=request.POST.get('username'))
                if user != request.user:
                    user_list.append(user)

            except:
                pass

        elif request.method == 'POST' and 'list' in request.POST or 'page' in request.GET:
            user_list = User.objects.exclude(username=request.user.username)

            paginator = Paginator(user_list, 10)
            page = request.GET.get('page')
            try:
                user_list = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                user_list = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                user_list = paginator.page(paginator.num_pages)

        admin_list = []
        blogger_list = []
        for user in user_list:
            admin_list.append(user_in_group(user, 'Admin'))
            blogger_list.append(user_in_group(user, 'Blogger'))

        users_zipped = zip(user_list, admin_list, blogger_list)

        data = {
            'user_list': user_list,
            'users_zipped': users_zipped,
            'admin': admin,
            'blogger': user_in_group(request.user, 'Blogger'),
            'page_header': 'Admin Panel',
            'page_subheader': 'User Management',
        }
        return render_to_response('admin.html', data, context_instance=RequestContext(request))
    else:
        return HttpResponse(status=403)


@ajax
def delete_user(request, user_id):

    admin = user_in_group(request.user, 'Admin')
    if admin:
        try:
            user = User.objects.get(id=user_id)
            if user == request.user:
                msg = 'You cannot delete yourself'
            else:
                user.delete()
                msg = 'success'
        except:
            return HttpResponse(status=404)

        return {
            'msg': msg,
            'user_id': user_id
        }
    else:
        return HttpResponse(status=403)


@ajax
def toggle_role(request, user_id, role):

    admin = user_in_group(request.user, 'Admin')
    if admin:
        try:
            user = User.objects.get(id=user_id)
            if user == request.user:
                msg = 'You cannot edit your permissions'
            else:

                edit_role(user, role)

                msg = 'success'
        except:
            return HttpResponse(status=404)

        return {
            'msg': msg,
            'role': role,
            'user_id': user_id
        }
    else:
        return HttpResponse(status=403)


def index(request):

    article_list = Article.list()
    return show_article_list(request, article_list, '')



def logout_view(request):
    logout(request)
    return redirect(index)


def my_articles(request):

    blogger = user_in_group(request.user, 'Blogger')
    if blogger:
        article_list = Article.my_article_list(request.user)
        return show_article_list(request, article_list, 'My Articles')
    else:
        return HttpResponse(status=403)


@login_required
def my_saved_articles(request):
    saved_article_list = SavedArticle.article_list(request.user)

    # get the articles list out of the saved articles list
    article_list = []
    for saved_article in saved_article_list:
        article_list.append(saved_article.article)

    return show_article_list(request, article_list, 'My Saved Articles')


@login_required
def my_favourite_articles(request):
    favourite_article_list = FavouriteArticle.article_list(request.user)

    # get the articles list out of the favourite articles list
    article_list = []
    for favourite_article in favourite_article_list:
        article_list.append(favourite_article.article)

    return show_article_list(request, article_list, 'My Favourite Articles')


def new_article(request):

    blogger = user_in_group(request.user, 'Blogger')
    if blogger:
        if request.method == 'POST':
            # if POST save the article
            form = ArticleForm(request.POST)
            if form.is_valid():
                article = form.save(commit=False)
                article.written_by = request.user
                article.save()
                return redirect(my_articles)
        else:
            # if GET create article form
            form = ArticleForm()

            data = {
                'page_header': 'My Articles',
                'page_subheader': 'New Article',
                'form': form,
                'admin': user_in_group(request.user, 'Admin'),
                'blogger': blogger
            }
            return render_to_response('new_edit_article.html', data, context_instance=RequestContext(request))
    else:
        return HttpResponse(status=403)


def view_article(request, article_id):
    try:
        article = Article.objects.get(id=article_id)
        article_list = [article]

    except:
        return HttpResponse(status=404)

    return show_article_list(request, article_list, '')


def edit_article(request, article_id):

    blogger = user_in_group(request.user, 'Blogger')
    admin = user_in_group(request.user, 'Admin')

    try:
        article = Article.objects.get(id=article_id)
        # an article can be edited by the user who wrote it or by an admin
        if article.written_by == request.user or admin:
            msg = False
        else:
            msg = "You cannot edit this article"
    except:
        return HttpResponse(status=404)

    if blogger:
        if request.method == 'POST':
            # if POST edit the article
            form = ArticleForm(request.POST, instance=article)
            if form.is_valid():
                article.header = form.cleaned_data['header']
                article.content = form.cleaned_data['content']
                article.save()
                return redirect(request.GET.get('next', None))
        else:
            # if GET create article form
            form = ArticleForm(instance=article)

            data = {
                'page_subheader': 'Edit Article',
                'from': request.GET.get('from', None),
                'form': form,
                'article': article,
                'msg': msg,
                'admin': admin,
                'blogger': blogger
            }
            return render_to_response('new_edit_article.html', data, context_instance=RequestContext(request))
    else:
        return HttpResponse(status=403)


@ajax
def delete_article(request, article_id):

    admin = user_in_group(request.user, 'Admin')

    try:
        article = Article.objects.get(id=article_id)
        # an article can be deleted by the user who wrote it or by an admin
        if article.written_by == request.user or admin:
            article.delete()
            msg = 'success'
        else:
            msg = 'You cannot delete this article'
    except:
        return HttpResponse(status=404)

    return {
        'msg': msg,
        'article_id': article_id
    }


@ajax
@login_required
def save_article(request, article_id):

    try:
        article = Article.objects.get(id=article_id)
        # delete the article from saved if it's already saved
        saved_article = SavedArticle.objects.filter(user=request.user, article=article_id)
        if saved_article:
            saved_article.delete()
        else:
            SavedArticle(user=request.user, article=article).save()
        msg = "success"
    except:
        return HttpResponse(status=404)

    return {
        'msg': msg,
        'article_id': article_id
    }


@ajax
@login_required
def favourite_article(request, article_id):

    try:
        article = Article.objects.get(id=article_id)
        # delete the article from saved if it's already saved
        favourite_article = FavouriteArticle.objects.filter(user=request.user, article=article_id)
        if favourite_article:
            favourite_article.delete()
        else:
            FavouriteArticle(user=request.user, article=article).save()
        msg = "success"
    except:
       return HttpResponse(status=404)

    return {
        'msg': msg,
        'article_id': article_id
    }


def user_in_group(user, group):
    """
    This function returns true if the user is in the selected group
    """
    group = Group.objects.get(name=group)
    up = UserPermissionList.objects.filter(user=user)
    try:
        return True if unicode(group.id) in up[0].group_fk_list else False
    except:
        return False


def show_article_list(request, article_list, page_header):
    """
    This function is called from all the views that need to render the article list
    """
    paginator = Paginator(article_list, 5)
    page = request.GET.get('page')
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        articles = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        articles = paginator.page(paginator.num_pages)

    # check if the articles are saved and favourite
    saved_articles = []
    favourite_articles = []
    for article in articles:
        saved_articles.append(article.is_saved(request.user))
        favourite_articles.append(article.is_favourite(request.user))

    articles_zipped = zip(articles, saved_articles, favourite_articles)

    data = {
        'page_header': page_header,
        'articles': articles,
        'articles_zipped': articles_zipped,
        'admin': user_in_group(request.user, 'Admin'),
        'blogger': user_in_group(request.user, 'Blogger'),
        'reader': user_in_group(request.user, 'Reader')
    }
    return render_to_response('article_list.html', data, context_instance=RequestContext(request))


def edit_role(user, role_name):
    """
    This function adds/removes an user from the group passed as parameter
    """

    admin = user_in_group(user, 'Admin')
    blogger = user_in_group(user, 'Blogger')

    if (role_name == 'admin'):
        group = Group.objects.get(name='Admin')
        role = admin
        aux = blogger
        aux_name = 'Blogger'
    else:
        group = Group.objects.get(name='Blogger')
        role = blogger
        aux = admin
        aux_name = 'Admin'

    if (role):
        # remove user from the group if the user already exists in the group
        groups = []
        groups.append(Group.objects.get(name='Reader'))
        if (aux):
            groups.append(Group.objects.get(name=aux_name))

        utils.update_user_groups(user, groups)

    else:
        # add user to the group
        utils.add_user_to_group(user, group)



