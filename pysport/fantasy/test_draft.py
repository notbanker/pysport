from .draft import salary_constrained_team, doubly_constrained_team

def test_salary_constrained_team():
    names        = ['bill','fred','barney']
    salaries     = [100., 200., 300.]
    forecasts    = [ 2.5, 2.5, 5.0 ]
    cap          = 400.
    chosen, team = salary_constrained_team( names=names, salaries=salaries,\
                                                   forecasts=forecasts, cap=cap,\
                                                   num_pick=2 )
    print team
    assert 'barney' in team
    assert 'bill' in team
    assert 'fred' not in team


def test_doubly_constrained_team():
    names        = ['bill','fred','barney','beth']
    salaries     = [100., 200., 300., 295.]
    forecasts    = [ 2.5, 2.5, 5.0, 5.0 ]
    cap          = 500.
    salaries1    = [ 1. , 0.,  0.,  1.]
    cap1         = 0.5
    chosen, team = doubly_constrained_team( names=names, salaries=salaries,\
                                                   forecasts=forecasts, cap=cap,\
                                                    salaries1=salaries1, cap1=cap1,\
                                                   num_pick=2 )
    print team
    assert 'barney' in team
    assert 'bill' not in team
    assert 'fred' in team
    assert 'beth' not in team
