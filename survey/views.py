# Matplotlibの設定を変更してGUIバックエンドを使わないようにする
import matplotlib
matplotlib.use('AGG')

import matplotlib.pyplot as plt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Count, F
from .forms import *
from accounts.models import Profile
from io import BytesIO

def index(request):
    return render(request, "index.html")

def survey_all(request):
    surveys = Survey.objects.all()
    context = {
        "surveys": surveys
    }
    return render(request, "survey_all.html", context)

@login_required
def create(request):
    # htmlでアンケートの詳細を5回だけ繰り返すための変数
    loop_times = list(range(1,6))

    if request.method == "POST":
        # それぞれのフォームデータを格納する
        survey_form = SurveyForm(request.POST)
        question_forms = [QuestionForm(request.POST, prefix=str(i)) for i in loop_times]
        choice_form_1 = [ChoiceForm(request.POST, prefix=f"choice_1_{i}") for i in loop_times]
        choice_form_2 = [ChoiceForm(request.POST, prefix=f"choice_2_{i}") for i in loop_times]
        choice_form_3 = [ChoiceForm(request.POST, prefix=f"choice_3_{i}") for i in loop_times]

        # question_formが全てis_validを満たすかどうか確認する
        if all(question_form.is_valid() for question_form in question_forms) and survey_form.is_valid():
            profile = Profile.objects.get(user=request.user)

            # surveyフォームをインスタンスにして、ユーザーを紐づける
            survey = survey_form.save(commit=False)
            survey.profile = profile
            survey.save()

            # questionフォームをインスタンスにして、surveyオブジェクトを紐づける
            for q_form, c_form_1, c_form_2, c_form_3 in zip(question_forms, choice_form_1, choice_form_2, choice_form_3):
                question = q_form.save(commit=False)
                question.survey = survey
                question.save()

                # 単一選択、複数選択の場合、各質問に対する選択肢を扱う
                if question.question_type in ['SC', 'MC'] and c_form_1.is_valid() and c_form_2.is_valid() and c_form_3.is_valid():
                    # choiceフォームをインスタンスにして、questionオブジェクトを紐づける
                    choice_1 = c_form_1.save(commit=False)
                    choice_2 = c_form_2.save(commit=False)
                    choice_3 = c_form_3.save(commit=False)
                    choice_1.question = question
                    choice_2.question = question
                    choice_3.question = question
                    choice_1.save()
                    choice_2.save()
                    choice_3.save()

            return redirect('my-survey')
    else:
        survey_form = SurveyForm()
        question_forms = [QuestionForm(prefix=str(i)) for i in loop_times]
        choice_form_1 = [ChoiceForm(prefix=f"choice_1_{i}") for i in loop_times]
        choice_form_2 = [ChoiceForm(prefix=f"choice_2_{i}") for i in loop_times]
        choice_form_3 = [ChoiceForm(prefix=f"choice_3_{i}") for i in loop_times]

        context = {
            "survey_form": survey_form,
            'forms': zip(question_forms, choice_form_1, choice_form_2, choice_form_3),
            "loop_times": loop_times,
        }
        return render(request, "create.html", context)

@login_required
def my_survey(request):
    profile = Profile.objects.get(user=request.user)
    surveys = Survey.objects.filter(profile=profile)
    context = {
        "surveys": surveys
    }
    return render(request, "my_survey.html", context)

# アンケート回答ページ
def survey_answer(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    questions = Question.objects.filter(survey=survey)

    # 初期化
    context = {
        "survey": survey,
        "errors": None,
    }
    answer_forms = []

    if request.method == "POST":
        is_all_valid = True    # 全てのフォームが有効かどうかをチェックするフラグ
        answer_forms = []   # POSTデータから生成されたフォームを保存するリスト

        # POSTリクエストの場合は、各質問に対して回答を保存
        for question in questions:
            form = AnswerForm(request.POST, question=question)
            if form.is_valid():
                answer = Answer.objects.create(question=question)
                if question.question_type == 'TX':
                    answer.text = form.cleaned_data[f"q_{question.id}"]
                elif question.question_type == 'SC':
                    answer.choice = form.cleaned_data[f"q_{question.id}"]
                elif question.question_type == 'MC':
                    answer.multiple_choices.set(form.cleaned_data[f"q_{question.id}"])
                elif question.question_type == 'RS':
                    answer.rating_score = form.cleaned_data[f"q_{question.id}"]

                answer.save()
            else:
                is_all_valid = False
            answer_forms.append((question, form))   # バリデーションエラーのあるフォームを追加

        if is_all_valid:
            return redirect('index')
        else:
            # 一つでも無効なフォームがあった場合、エラーメッセージとともにフォームを再表示
            context["errors"] = "入力内容に誤りがあります"
    else:
        # GETリクエストの場合は、各質問に対する空のフォームを生成
        answer_forms = []
        for question in questions:
            answer_form = AnswerForm(question=question)
            answer_forms.append((question, answer_form))   # question,formのペアのタプルを生成
    context["answer_forms"] = answer_forms
    return render(request, "survey_answer.html", context)

def delete(request, pk):
    survey = get_object_or_404(Survey, id=pk)
    if request.method == 'POST':
        survey.delete()
        return redirect('my-survey')
    else:
        context = {
            "survey": survey,
        }
        return render(request, "delete.html", context)

def survey_result(request, pk):
    survey = get_object_or_404(Survey, id=pk)
    context = {
        "survey": survey,
    }
    return render(request, "survey_result.html", context)

def survey_chart(request, pk):
    survey = get_object_or_404(Survey, id=pk)
    questions = survey.questions.all()
    fig, axs = plt.subplots(len(questions), figsize=(10, 5 * len(questions)))

    for i, question in enumerate(questions):
        answers = Answer.objects.filter(question=question)

        if question.question_type == 'SC':
            data = answers.values(choice_text=F('choice__text')).annotate(total=Count('choice'))
            labels = [d['choice_text'] for d in data]
            counts = [d['total'] for d in data]
            axs[i].bar(labels, counts, color="blue")
        elif question.question_type == 'MC':
            choices = Choice.objects.filter(question=question)
            choice_counts = {choice.text: 0 for choice in choices}
            for answer in answers:
                selected_choices = answer.multiple_choices.all()
                for choice in selected_choices:
                    choice_counts[choice.text] += 1
            labels = list(choice_counts.keys())
            counts = list(choice_counts.values())
            axs[i].bar(labels, counts, color="orange")
        elif question.question_type == 'RS':
            data = answers.values('rating_score').annotate(total=Count('rating_score'))
            labels = [str(d['rating_score']) for d in data]
            counts = [d['total'] for d in data]
            axs[i].bar(labels, counts, color='green')
        elif question.question_type == 'TX':
            data = answers.count()
            labels =['Response']
            counts = [data]
            axs[i].bar(labels, counts, color="purple")

        axs[i].set_title(question.text)
        axs[i].set_ylabel('Count')

        # Y軸の目盛りを調整（最大値に余裕を持たせる）
        axs[i].set_ylim(0, max(counts) + 1)
        axs[i].set_yticks(range(0, max(counts) + 2, 1)) # 1刻みで目盛りを表示

    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return HttpResponse(buf, content_type='image/png')