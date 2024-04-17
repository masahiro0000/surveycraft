from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import *
from accounts.models import Profile

def index(request):
    return render(request, "index.html")

@login_required
def create(request):
    if request.method == "POST":
        survey_form = SurveyForm(request.POST)
        question_form = QuestionForm(request.POST)
        choice_form = ChoiceForm(request.POST)
        rating_form = RatingForm(request.POST)
        if question_form.is_valid() and survey_form.is_valid() and choice_form.is_valid() and rating_form.is_valid():

            # Profileオブジェクトを取得
            profile = Profile.objects.get(user=request.user)

            # surveyフォームをインスタンスにして、ユーザーを紐づける
            survey = survey_form.save(commit=False)
            survey.profile = profile
            survey.save()

            # questionフォームをインスタンスにして、surveyオブジェクトを紐づける
            question = question_form.save(commit=False)
            question.survey = survey
            question.save()

            # choiceフォームをインスタンスにして、questionオブジェクトを紐づける
            choice = choice_form.save(commit=False)
            choice.question = question
            choice.save()

            # ratingフォームをインスタンスにして、questionオブジェクトを紐づける
            rating = rating_form.save(commit=False)
            rating.question = question
            rating.save()

            return redirect('my-survey')
    else:
        survey_form = SurveyForm()
        question_form = QuestionForm()
        choice_form = ChoiceForm()
        rating_form = RatingForm()

        # htmlでアンケートの詳細を5回だけ繰り返すための変数
        loop_times = list(range(1,6))

        context = {
            "survey_form": survey_form,
            "question_form": question_form,
            "choice_form": choice_form,
            "rating_form": rating_form,
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