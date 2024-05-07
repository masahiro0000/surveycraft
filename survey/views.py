from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import *
from accounts.models import Profile
from django.forms import modelformset_factory
import uuid

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
    if request.method == "POST":
        # POSTリクエストの場合は、各質問に対して回答を保存
        for question in questions:
            answer_form = AnswerForm(request.POST, question=question)
            if answer_form.is_valid():
                answer_form.save(commit=False)
                answer_form.question = question
                answer_form.save()
        return redirect('index')
    else:
        # GETリクエストの場合は、各質問に対する空のフォームを生成
        answer_forms = []
        for question in questions:
            choices = Choice.objects.filter(question=question)
            answer_form = AnswerForm(question=question)
            answer_forms.append((question, answer_form, choices))   # question,formのペアのタプルを生成
        context = {
            "survey": survey,
            "answer_forms": answer_forms,
        }
        return render(request, "survey_answer.html", context)