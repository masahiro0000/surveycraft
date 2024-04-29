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
    #loop_times = 5

    if request.method == "POST":
        survey_form = SurveyForm(request.POST)
        question_forms = [QuestionForm(request.POST, prefix=str(i)) for i in loop_times]
        choice_form = ChoiceForm(request.POST)
        #rating_form = RatingForm(request.POST)
        #if question_form.is_valid() and survey_form.is_valid() and choice_form.is_valid() and rating_form.is_valid():

        # question_formが全てis_validを満たすかどうか確認する
        question_form_valid = True
        for form in question_forms:
            if not form.is_valid():
                question_form_valid = False

        if question_form_valid and survey_form.is_valid() and choice_form.is_valid():

            # Profileオブジェクトを取得
            profile = Profile.objects.get(user=request.user)

            # surveyフォームをインスタンスにして、ユーザーを紐づける
            survey = survey_form.save(commit=False)
            survey.profile = profile
            survey.save()

            # questionフォームをインスタンスにして、surveyオブジェクトを紐づける
            for form in question_forms:
                question = form.save(commit=False)
                question.survey = survey
                question.save()

                if question.question_type in ['SC', 'MC']:  # 単一選択、複数選択の場合
                    # choiceフォームをインスタンスにして、questionオブジェクトを紐づける
                    choice = choice_form.save(commit=False)
                    choice.question = question
                    choice.save()

            # ratingフォームをインスタンスにして、questionオブジェクトを紐づける
            #rating = rating_form.save(commit=False)
            #rating.question = question
            #rating.save()

            return redirect('my-survey')
    else:
        survey_form = SurveyForm()
        question_forms = [QuestionForm(prefix=str(i)) for i in loop_times]
        #question_forms = QuestionForm()
        choice_form = ChoiceForm()
        #rating_form = RatingForm()

        context = {
            "survey_form": survey_form,
            "question_forms": question_forms,
            "choice_form": choice_form,
            #"rating_form": rating_form,
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
#def survey_answer(request, pk):
#    survey = get_object_or_404(Survey, pk=pk)
#    questions = Question.objects.filter(survey=survey)  # 該当するアンケートの質問を取得
#    if request.method == "POST":
#        # POSTリクエストの場合は、各質問に対して回答を保存
#        for question in questions:
#            question_data = {
#                'question': question.id,
#                'text': request.POST.get(f'text_{question.id}', None),
#                'choice': request.POST.get(f'choice_{question.id}', None),
#                'choices': request.POST.get(f'choices_{question.id}', None),
#                'rating': request.POST.get(f'rating_{question.id}', None)
#            }
#            answer_form = AnswerForm(question_data)
#            if answer_form.is_valid():
#                answer = answer_form.save(commit=False)
#                answer.question = question
#                answer.save()
#
#        return redirect('index')
#    else:
#        # GETリクエストの場合は、各質問に対する空のフォームを生成
#        answer_forms = []
#        for question in questions:
#            form = AnswerForm(initial={'question': question.id})
#            answer_forms.append((question, form))    # question,formのペアのタプルを生成
#        context = {
#            "survey": survey,
#            "answer_forms": answer_forms,
#        }
#        return render(request, "survey_answer.html", context)

def survey_answer(request, pk):
    survey = get_object_or_404(Survey, pk=pk)
    questions = Question.objects.filter(survey=survey)
    if request.method == "POST":
        # POSTリクエストの場合は、各質問に対して回答を保存
        for question in questions:
            form = AnswerForm(request.POST, question=question)
            if form.is_valid():
                form.save(commit=False)
                form.question = question
                form.save()
        return redirect('index')
    else:
        # GETリクエストの場合は、各質問に対する空のフォームを生成
        answer_forms = []
        for question in questions:
            form = AnswerForm(initial={'question': question.id})
            answer_forms.append((question, form))   # question,formのペアのタプルを生成
        context = {
            "survey": survey,
            "answer_forms": answer_forms,
        }
        return render(request, "survey_answer.html", context)