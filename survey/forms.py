from django import forms
from .models import Question, Choice, Rating, Survey, Answer

class SurveyForm(forms.ModelForm):
    title = forms.CharField(label="タイトル", widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "タイトル"}))
    description = forms.CharField(label="説明", widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "アンケートの説明"}))
    class Meta:
        model = Survey
        fields = ['title', 'description']

class QuestionForm(forms.ModelForm):
    question_type = forms.ChoiceField(
        label="質問形式",
        choices=Question.QUESTION_TYPE,   #モデルから選択肢を引き継ぎ
        widget=forms.Select(attrs={"class": "form-control"})
        )
    text = forms.CharField(
        label="質問内容",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "質問内容を入力してください"})
        )
    is_required = forms.BooleanField(
        label="回答必須",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )
    class Meta:
        model = Question
        fields = ['question_type', 'text', 'is_required']

class ChoiceForm(forms.ModelForm):
    text1 = forms.CharField(
        label="選択肢1",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "選択肢1"})
    )
    text2 = forms.CharField(
        label="選択肢2",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "選択肢2"})
    )
    text3 = forms.CharField(
        label="選択肢3",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "選択肢3"})
    )
    class Meta:
        model = Choice
        fields = ['text1', 'text2', 'text3']    # 3つの選択肢

class RatingForm(forms.ModelForm):
    text1 = forms.CharField(
        label="評価軸1",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "評価軸1"})
    )
    text2 = forms.CharField(
        label="評価軸2",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "評価軸2"})
    )
    text3 = forms.CharField(
        label="評価軸3",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "評価軸3"})
    )
    class Meta:
        model = Rating
        fields = ['text1', 'text2', 'text3']    # 3つの評価軸を設定

class AnswerForm(forms.ModelForm):
    text = forms.CharField(label="回答", widget=forms.TextInput(attrs={"class": "form-control"}))
    class Meta:
        model = Answer
        fields = ['question', 'text', 'choice', 'rating']
