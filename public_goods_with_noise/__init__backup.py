from otree.api import *



class Constants(BaseConstants):
    name_in_url = 'public_goods_with_noise'
    players_per_group = 4
    num_rounds = 2
    endowment0 = 50
    endowment1 = 100
    multiplier = 1.8

    #STORING PAGE INFORMATION
    Contribute0_template = 'public_goods_with_noise/Contribute0.html'
    Contribute1_template = 'public_goods_with_noise/Contribute1.html'


class Player(BasePlayer):
    contribution = models.CurrencyField(
        min=0, label="How much will you contribute?"
    )

    def contribution_max(self):
        if self.type == 0:
            return Constants.endowment0
        else:
            return Constants.endowment1

    nr = models.IntegerField()
    noiseS = models.IntegerField()
    noiseO = models.IntegerField()
    r = models.IntegerField()
    type = models.IntegerField() #0=poor; 1=rich
    sametype = models.CurrencyField()
    othertype = models.CurrencyField()
    pertsame = models.CurrencyField()
    pertother = models.CurrencyField()
    endowment = models.CurrencyField()
    selfdisplay = models.IntegerField()


class Subsession(BaseSubsession):
    def creating_session(self):
        pl = self.get_players()
        print(pl)
        for player in self.get_players():
            player.type2 = 34 #next(types)
        print('somebullshit')


class Group(BaseGroup):
    total_contribution = models.CurrencyField()
    individual_share = models.CurrencyField()


# FUNCTIONS
def set_payoffs(group: Group):
    players = group.get_players()
    contributions = [p.contribution for p in players]
    group.total_contribution = sum(contributions)
    group.individual_share = (
        group.total_contribution * Constants.multiplier / Constants.players_per_group
    )
    for p in players:
        p.payoff = p.endowment - p.contribution + group.individual_share
        p.sametype = sum(p2.contribution for p2 in players if (p2 != p and p.type == p2.type))
        p.othertype = sum([p2. contribution for p2 in players if (p.type != p2.type)])/2


# PAGES
class Roundintro(Page): #this is working as of 15.9 at 19.47
    def before_next_page(player: Player, timeout_happened):
        player.r = player.round_number
        pl = player.group.get_players()
        if player.r == 1:
            import itertools
            types = itertools.cycle([0, 1]) #0=poor; 1=rich
            for p in pl:
                p.type = next(types)
            if player.type == 0:
                player.endowment = Constants.endowment0
            else:
                player.endowment = Constants.endowment1
#   SHOULD WORK NOW. TRY TOMORROW
            alltype0 = [p for p in player.subsession.get_players() if p.type == 0]
            alltype1 = [p for p in player.subsession.get_players() if p.type == 1]
            selfdisplays = itertools.cycle([0, 1])
            for guy in alltype0:
                guy.selfdisplay = next(selfdisplays)
            for guy in alltype1:
                guy.selfdisplay = next(selfdisplays)

        if player.r != 1:
            import random
            player.noiseS = random.randint(-3, 3)
            player.noiseO = random.randint(-3, 3)
            prev_player = player.in_round(player.r - 1)
            player.selfdisplay = prev_player.selfdisplay
            player.type = prev_player.type
            player.endowment = prev_player.endowment
            if prev_player.sametype + player.noiseS < 0:
                player.pertsame = 0
            elif prev_player.sametype + player.noiseS > player.endowment:
                player.pertsame = player.endowment
            else:
                player.pertsame = prev_player.sametype + player.noiseS

            if prev_player.othertype + player.noiseO <0:
                player.pertother = 0
            elif player.type == 0 and prev_player.othertype + player.noiseO > Constants.endowment1:
                player.pertother = Constants.endowment1
            elif player.type == 1 and prev_player.othertype + player.noiseO > Constants.endowment0:
                player.pertother = Constants.endowment0
            else:
                player.pertother = prev_player.othertype + player.noiseO


class Contribute(Page):
    form_model = 'player'
    form_fields = ['contribution']
#    def before_next_page(player: Player, timeout_happened):
#        import random
#        player.noiseH = random.randint(-3, +3)
#        player.noiseP = random.randint(-3, 3)


#class Buffer(WaitPage):
#    after_all_players_arrive = makenoise


class ResultsWaitPage(WaitPage):
    after_all_players_arrive = set_payoffs


class Results(Page):
    pass


page_sequence = [Roundintro, Contribute, ResultsWaitPage, Results]
