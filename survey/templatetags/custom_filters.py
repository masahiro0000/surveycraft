

from django import template

register = template.Library()

@register.filter
def get_dynamic_field(answer_form, question_id):
    return answer_form[f"q_{question_id}"]