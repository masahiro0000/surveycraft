from django import forms
from .models import Question, Choice, Survey, Answer

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
    text = forms.CharField(
        label="選択肢",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "選択肢"})
    )
    class Meta:
        model = Choice
        fields = ['text']

class AnswerForm(forms.ModelForm):
    text = forms.CharField(
        label="回答",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        required=False,
    )
    choice = forms.ModelChoiceField(
        queryset=Choice.objects.none(),
        label="選択肢",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
    )
    multiple_choices = forms.ModelMultipleChoiceField(
        queryset=Choice.objects.none(),
        label="複数選択式",
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    rating_score = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)], # 1から5までの評価スコアを選択肢として設定
        label="評価スコア",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=False,
    )
    class Meta:
        model = Answer
        #fields = ['text', 'choice', 'multiple_choices', 'rating_score']
        fields = [] # 空に設定し、__init__でフィールドを動的に追加

    def __init__(self, *args, **kwargs):
        question = kwargs.pop('question', None) # 質問インスタンスをキーワード引数から取り出す
        super().__init__(*args, **kwargs)

        if question is not None:
            if question.question_type == 'TX':  # テキスト回答
                self.fields['text'].required = True # 必須回答にする
            elif question.question_type == 'SC':    #単一選択式の場合
                self.fields['choice'].queryset = Choice.objects.filter(question=question)   # 特定の質問に関連する選択肢のみを表示するためにフィルタする
                self.fields['choice'].required = True
            elif question.question_type == 'MC':    #複数選択式の場合
                self.fields['multiple_choices'].queryset = Choice.objects.filter(question=question)
                self.fields['multiple_choices'].required = True
            elif question.question_type == 'RS':    # 評価スコア
                self.fields['rating_score'].required = True
