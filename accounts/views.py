from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from .forms import CustomLoginForm, CustomUserCreationForm

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, 'ログインに成功しました')
                return redirect('index')
            else:
                messages.error(request, 'ユーザー名またはパスワードが間違っています')
        else:
            # フォームのバリデーションエラーをハンドル
            messages.error(request, '入力に誤りがあります')
    else:
        form = CustomLoginForm()

    context = {
        "form": form,
    }

    #POSTリクエストでない場合、またはログイン失敗時にログインフォームを表示
    return render(request, 'login.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            #ユーザー認証
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")   #password1,2があるが、1を使用
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, '登録完了しました')
                return redirect('index')
        else:
            messages.error(request, "登録できませんでした。もう一度試してください。")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {"form": form})