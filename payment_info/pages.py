from ._builtin import Page, WaitPage
from otree.api import Currency as c, currency_range
from .models import Constants


class PaymentInfo(Page):

    form_model = 'player'
    form_fields = ['email']

    def before_next_page(self):
        self.player.payment = self.participant.final_payment_euros

    def vars_for_template(self):
        participant = self.participant
        return dict(
            redemption_code=participant.label or participant.code,
            payment = participant.final_payment_euros
        )


page_sequence = [PaymentInfo]
