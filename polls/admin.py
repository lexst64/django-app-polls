from django.contrib import admin

from .models import Question, Choice


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0
    min_num = 2


def upper_case_field(field: str,
                     boolean=None,
                     ordering=None,
                     description=None,
                     empty_value=None):
    @admin.display(
        boolean=boolean,
        ordering=ordering,
        description=description,
        empty_value=empty_value,
    )
    def inner_upper_case_field(model):
        return model.__dict__[field].upper()

    return inner_upper_case_field


class QuestionAdmin(admin.ModelAdmin):
    list_filter = ['pub_date']
    search_fields = ['question_text']
    search_help_text = 'Search by question text'
    list_display = ('question_text',
                    upper_case_field('question_author',
                                     ordering='question_author',
                                     description='Author'),
                    'was_published_recently',
                    'pub_date')
    fieldsets = [
        ('Info', {'fields': ['question_author', 'question_text']}),
        ('Date', {'fields': ['pub_date']})
    ]
    inlines = [ChoiceInline]


admin.site.register(Question, QuestionAdmin)
