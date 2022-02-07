import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question, Choice


def create_choice(question: Question, choice_text, votes: int = 0):
    return question.choice_set.create(choice_text=choice_text, votes=votes)


def get_choice_by_pk(pk):
    return Choice.objects.get(pk=pk)


def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(
        question_text=question_text,
        question_author='admin',
        pub_date=time,
    )


class QuestionIndexViewTests(TestCase):
    def test_no_question(self):
        res = self.client.get(reverse('polls:index'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'there are no active polls here')
        self.assertQuerysetEqual(res.context['all_question_objects'], [])

    def test_past_question(self):
        question = create_question(question_text='past', days=-30)
        res = self.client.get(reverse('polls:index'))
        self.assertEqual(res.status_code, 200)
        self.assertQuerysetEqual(
            res.context['all_question_objects'],
            [question],
        )

    def test_future_question(self):
        create_question(question_text='future', days=30)
        res = self.client.get(reverse('polls:index'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'there are no active polls here')
        self.assertContains(res, 'Polls waiting to be published: 1')
        self.assertQuerysetEqual(
            res.context['all_question_objects'],
            [],
        )

    def test_future_question_and_past_question(self):
        create_question(question_text='future', days=10)
        past_question = create_question(question_text='past', days=-4)
        res = self.client.get(reverse('polls:index'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'Polls waiting to be published: 1')
        self.assertQuerysetEqual(res.context['all_question_objects'], [past_question])

    def test_two_past_questions(self):
        question1 = create_question(question_text='past1', days=-3)
        question2 = create_question(question_text='past2', days=-10)
        res = self.client.get(reverse('polls:index'))
        self.assertEqual(res.status_code, 200)
        self.assertQuerysetEqual(
            res.context['all_question_objects'],
            [question1, question2],
        )

    def test_two_future_questions(self):
        """
        Future questions (with the date which is greater than current date)
        mustn't be available on the index page (index.html).
        But there must be text telling how many
        polls are waiting for publishing
        """
        create_question(question_text='future1', days=3)
        create_question(question_text='future2', days=10)
        res = self.client.get(reverse('polls:index'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'there are no active polls here')
        self.assertContains(res, 'Polls waiting to be published: 2')
        self.assertQuerysetEqual(res.context['all_question_objects'], [])


class QuestionVoteViewTests(TestCase):
    def post_form_data(self, question_id, data):
        url = reverse('polls:vote', args=(question_id,))
        content_type = 'application/x-www-form-urlencoded'
        return self.client.post(url, data=data, content_type=content_type)

    def assert_choices_votes(self, choices: dict[int, int]):
        for choice_id, expected_votes in choices.items():
            choice = get_choice_by_pk(choice_id)
            self.assertEqual(choice.votes, expected_votes)

    def test_selected_choice_with_existing_question(self):
        question = create_question(question_text='text', days=-1)
        choice1 = create_choice(question, 'choice1')
        choice2 = create_choice(question, 'choice2')

        res = self.post_form_data(question.id, data='choice=%s' % choice1.id)

        self.assertEqual(res.status_code, 302)
        self.assert_choices_votes({choice1.id: 1, choice2.id: 0})

    def test_not_selected_choice_with_existing_question(self):
        question = create_question(question_text='text', days=-5)
        choice1 = create_choice(question, 'choice1')
        choice2 = create_choice(question, 'choice2')

        res = self.post_form_data(question.id, data='')

        self.assertEqual(res.status_code, 200)
        self.assertContains(res, question.question_text)
        self.assert_choices_votes({choice1.id: 0, choice2.id: 0})

    def test_selected_choice_with_wrong_form_input(self):
        question = create_question(question_text='text', days=-5)
        choice1 = create_choice(question, 'choice1')
        choice2 = create_choice(question, 'choice2')

        res = self.post_form_data(question.id, data='choise=%s' % choice2.id)

        self.assertEqual(res.status_code, 200)
        self.assertContains(res, question.question_text)
        self.assert_choices_votes({choice1.id: 0, choice2.id: 0})

    def test_selected_not_existing_choice(self):
        question = create_question(question_text='text', days=0)
        choice1 = create_choice(question, 'choice1')
        choice2 = create_choice(question, 'choice2')

        res = self.post_form_data(question.id, data='choice=32')

        self.assertEqual(res.status_code, 200)
        self.assertContains(res, question.question_text)
        self.assert_choices_votes({choice1.id: 0, choice2.id: 0})

    def test_selected_choice_for_not_existing_question(self):
        question = create_question(question_text='text', days=0)
        choice1 = create_choice(question, 'choice1')
        choice2 = create_choice(question, 'choice2')

        res = self.post_form_data(question_id=2, data='choice=%s' % choice2.id)

        self.assertEqual(res.status_code, 404)
        self.assert_choices_votes({choice1.id: 0, choice2.id: 0})


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of future question is not available
        and server responses with 404 status code
        """
        question = create_question(question_text='future', days=4)
        url = reverse('polls:detail', args=[question.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)

    def test_past_question(self):
        """
        The detail view of past question is available
        and server responses with 200 status code.
        HTML contains question text as well
        """
        question = create_question(question_text='past', days=-17)
        url = reverse('polls:detail', args=[question.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, question.question_text)


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)
