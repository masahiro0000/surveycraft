from django.db import models
from django.urls import reverse
from accounts.models import Profile

class Survey(models.Model):
    profile = models.ForeignKey(
        Profile,
        related_name="surveys",
        on_delete=models.CASCADE
        )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

    # アンケート回答ページのURL生成
    @property
    def get_absolute_url(self):
        return reverse('survey-answer', args=[self.pk])

class Question(models.Model):
    TEXT = 'TX'
    SINGLE_CHOICE = 'SC'
    MULTIPLE_CHOICE = 'MC'
    RATING_SCORE = 'RS'
    QUESTION_TYPE = [
        (TEXT, 'テキスト入力'),
        (SINGLE_CHOICE, '単一選択式'),
        (MULTIPLE_CHOICE, '複数選択式'),
        (RATING_SCORE, '評価スケール(1~5の評価スコア)'),
    ]

    survey = models.ForeignKey(
        Survey,
        related_name="questions",
        on_delete=models.CASCADE
        )
    text = models.CharField(
        max_length=255,
        verbose_name='質問文'
        )
    question_type = models.CharField(
        max_length=2,
        choices=QUESTION_TYPE,
        default=TEXT
        )
    is_required = models.BooleanField(
        default=False,
        verbose_name="必須質問"
        )

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name="choices", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)    # 選択肢のテキスト

    def __str__(self):
        return self.text

class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
        )
    text = models.TextField(
        blank=True,
        null=True
        )
    choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="single_choice"
        )
    multiple_choices = models.ManyToManyField(
        Choice,
        blank=True,
        related_name="multiple_choices"
        )
    rating_score = models.PositiveIntegerField(
        choices=[(i, str(i)) for i in range(1,6)],
        blank=True,
        null=True,
        )

    def __str__(self):
        if self.question.question_type == Question.SINGLE_CHOICE and self.choice:
            return f"Single Choice Answer: {self.choice.text}"
        elif self.question.question_type == Question.MULTIPLE_CHOICE and self.multiple_choices.exists():
            choices_texts = ', '.join(choice.text for choice in self.multiple_choices.all())
            return f"Multiple Choice Answers: {choices_texts}"
        elif self.question.question_type == Question.RATING_SCORE and self.rating_score:
            return f"Rating Scale: {self.rating_score}"
        elif self.text:
            return f"Text Answer: {self.text}"
        else:
            return "Empty Answer"
