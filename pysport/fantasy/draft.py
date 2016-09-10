import pulp

# Drafting fantasy teams

def salary_constrained_team( names, salaries, forecasts, cap, num_pick = 6 ):
    """ Maximizes mean forecast subject to salary constraint only

        :param names         [ str ]
        :param salaries      [ float ]
        :param forecasts     [ float ]
        :param salary_cap    float
        :param num_pick      int
        :returns
            chosen [ bool ]   Boolean vector indicating whether player was chosen
            team   [ str ]    List of chosen player names

    """
    return doubly_constrained_team(names=names, salaries=salaries, forecasts=forecasts, cap=cap, salaries1=None, cap1=None, num_pick=num_pick)

def doubly_constrained_team(names, salaries, forecasts, cap=50000, salaries1=None, cap1=None, num_pick = 6):
    """ Maximizes mean forecast subject to two different salary constraints
        The second salary and cap can be interpreted as an additional penalty for player reuse, for example.

        :param names  [ str ]
        :param salaries      [ float ]
        :param forecasts     [ float ]
        :param cap        float
        :param salaries1     [ float ]
        :param cap1       float
        :param forecasts     [ float ]
        :param salary_cap    float

        :param num_pick      int
        :returns
            chosen [ bool ]   Boolean vector indicating whether player was chosen
            team   [ str ]    List of chosen player names

    """
    prob = _pulp_problem(names=names, salaries=salaries, forecasts=forecasts, cap=cap, num_pick=num_pick,\
                         salaries1=salaries1, cap1=cap1 )
    prob.solve()
    team = list()
    names = list()
    for var in prob.variables():
        if var.value() == 1:
            team.append(var.name[7:].replace('_', ' '))
            names.append(var.name[7:])
    chosen = [nm in team for nm in names]
    return chosen, team


def _pulp_problem(names, salaries, forecasts, cap = 50000, num_pick = 6, salaries1=None, cap1 = None):
    """ Maximize points per game subject to salary cap

        :param names  [ str ]
        :param salaries      [ float ]
        :param forecasts     [ float ]
        :param cap    float
        :param num_pick      int
        :param salaries1  [ float ]   A weight assigned to each player (.e.g to constrains reuse)
        :param cap1  float         A constraint on weighted reuse
        :returns
            prob     A Pulp Problem object encapsulating the optimization problem
    """
    prob     = pulp.LpProblem( "Draft picking problem", pulp.LpMaximize )
    assert len(names)==len(salaries),"Should be the same number of players as salaries"
    salary   = dict(zip(names, salaries))
    assert len(forecasts)==len(names),"Should be the same number of players as forecasts"
    ppg      = dict(zip(names, forecasts))
    selected = pulp.LpVariable.dicts("Choice", names, 0, 1, pulp.LpInteger)
    prob    += pulp.lpSum([selected[p] * ppg[p] for p in names]), "Sum of negative points per game"
    prob    += pulp.lpSum([selected[p] * salary[p] for p in names]) <= cap, "Sum of salaries must be below CAP"
    prob    += pulp.lpSum([selected[p] for p in names]) == num_pick, "Must pick " + str(num_pick) + " players"
    if (salaries1 is not None) and (cap1 is not None):
        assert len(salaries1)==len(names),"Should be the same number of players as second salaries"
        salary1 =  dict(zip(names, salaries1))
        prob += pulp.lpSum([selected[p] * salary1[p] for p in names]) <= cap1

    return prob