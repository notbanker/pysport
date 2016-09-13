

###########################################################################
#                                                                         #
#  This module provides a very simple way to select your fantasy teams,   #
#  assuming you have forecasts of their performances                      #
#                                                                         #
###########################################################################


# We suppose that the following players ...
names        = ['bill' ,'fred' ,'barney']

# ... have been assigned salaries
salaries     = [100., 200., 300.]

# ... and that your estimates for their performance are:
forecasts    = [ 2.5, 2.5, 5.0 ]

# Assuming a total salary cap of
cap          = 400.

# ... we wish to choose a team of two players to mazimise the sum of forecast scores.
from pysport.fantasy.draft import salary_constrained_team
chosen, team = salary_constrained_team( names=names, salaries=salaries, \
                                        forecasts=forecasts, cap=cap, \
                                        num_pick=2 )

# That's all:
print "Your team is " + str( team )