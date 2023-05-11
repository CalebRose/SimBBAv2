from random import choices
ticket_amounts = [.14, .14, .14, .125, .105, .09, .075, .06, .045, .03, .02, .015, .01, .005]
teams = [ i + 1 for i in range(14)]
for i in range(12):
    probabilities = [count/sum(ticket_amounts) for count in ticket_amounts]
    team_picked = choices(teams, probabilities)[0]
    print("The #{} Overall Pick goes to Team {}".format(12 - i, team_picked))
    # update probabilities by discarding all the tickets
    # belonging to picked team
    ticket_amounts[team_picked-1] = 0