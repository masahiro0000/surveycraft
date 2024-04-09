from django.db import models

class Question(models.Model):
    TEXT = 'TX'
    SINGLE_CHOICE = 'SC'
    MULTIPLE_CHOICE = 'MC'
    RATING_SCALE = 'RS'
    QUESTION_TYPE = [
        (TEXT, 'Text'),
        (SINGLE_CHOICE, 'Single choice'),
        (MULTIPLE_CHOICE, 'Multiple choice'),
        (RATING_SCALE, 'Rating scale'),
    ]

    text = models.CharField(max_length=255, verbose_name='質問文')
    question_type = models.CharField(max_length=2, choices=QUESTION_TYPE, default=TEXT)
    is_required = models.BooleanField(default=False, verbose_name="必須質問")

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, related_name="choices", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text

class Survey(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    questions = models.ManyToManyField(Question)

    def __str__(self):
        return self.title

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, blank=True, null=True, related_name="single_choice")
    choices = models.ManyToManyField(Choice, blank=True, related_name="multiple_choices")
    rating = models.IntegerField(blank=True, null=True)

    def __str__(self):
        if self.question.question_type == Question.SINGLE_CHOICE and self.choice:
            return f"Single Choice Answer: {self.choice.text}"
        elif self.question.question_type == Question.MULTIPLE_CHOICE and self.choices.exists():
            choices_texts = ', '.join(choice.text for choice in self.choices.all())
            return f"Multiple Choice Answers: {choices_texts}"
        elif self.question.question_type == Question.RATING_SCALE and self.rating:
            return f"Rating Scale: {self.rating}"
        elif self.text:
            return f"Text Answer: {self.text}"
        else:
            return "Empty Answer"
