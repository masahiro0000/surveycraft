from django import forms
from .models import Question, Choice, Rating, Survey, Answer

class SurveyForm(forms.ModelForm):
    title = forms.CharField(
        label="タイトル",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "タイトル"}))
    description = forms.CharField(
        label="説明",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "アンケートの説明"}))
    class Meta:
        model = Survey
        fields = ['title', 'description']

class QuestionForm(forms.ModelForm):
    text = forms.CharField(
        label="質問内容",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "質問内容を入力してください"})
        )
    question_type = forms.ChoiceField(
        label="質問形式",
        choices=Question.QUESTION_TYPE,   #モデルから選択肢を引き継ぎ
        widget=forms.Select(attrs={"class": "form-control"})
    )
    is_required = forms.BooleanField(
        label="回答必須",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"})
    )
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'is_required']

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

#class RatingForm(forms.ModelForm):
#    rating_score = forms.CharField(
#        label="評価",
#        required=False,
#        widget=forms.TextInput(attrs={"class": "form-control"})
#    )
#    text1 = forms.CharField(
#        label="評価軸1",
#        required=False,
#        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "評価軸1"})
#    )
#    text2 = forms.CharField(
#        label="評価軸2",
#        required=False,
#        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "評価軸2"})
#    )
#    text3 = forms.CharField(
#        label="評価軸3",
#        required=False,
#        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "評価軸3"})
#    )
#    class Meta:
#        model = Rating
#        fields = ['text1', 'text2', 'text3']    # 3つの評価軸を設定

class AnswerForm(forms.ModelForm):
    text = forms.CharField(
        label="回答",
        widget=forms.TextInput(attrs={"class": "form-control"}))
    choice = forms.ModelChoiceField(
        queryset=Choice.objects.all(),
        label="選択肢",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    choices = forms.ModelMultipleChoiceField(
        queryset=Choice.objects.all(),
        label="複数選択式",
        widget=forms.CheckboxSelectMultiple(),
    )
    rating_score = forms.ChoiceField(
        label="評価スコア",
        choices=[(i, str(i)) for i in range(1, 6)]  # 1~5の評価スコアから選択
    )
    class Meta:
        model = Answer
        fields = ['text', 'choice', 'choices', 'rating_score']

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question', None) # 質問インスタンスをキーワード引数から取り出す
        super(AnswerForm, self).__init__(*args, **kwargs)

        if question is not None:
            if question.question_type == 'TX':  #テキストフィールドの場合
                self.fields['text'].required = True # テキストフィールドを必須にする
            elif question.question_type == 'SC':    #単一選択式の場合
                self.fields['choice'].required = True
                self.fields['choice'].queryset = Choice.objects.filter(question=question)   # 特定の質問に関連する選択肢のみを表示するためにフィルタする
            elif question.question_type == 'MC':    #複数選択式の場合
                self.fields['choices'].required = True
                self.fields['choices'].queryset = Choice.objects.filter(question=question)
            elif question.question_type == 'RS':    #評価スケールの場合
                self.fields['rating_score'].required = True
            else:
                # 認識されない質問タイプの場合は、すべてのフィールドを非表示にする
                for field_name in ['text', 'choice', 'choices', 'rating_score']:
                    self.fields[field_name].widget = forms.HiddenInput()