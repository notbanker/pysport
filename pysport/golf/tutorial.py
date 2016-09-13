########################################################################################################
#                                                                                                      #
#   The module provides one solution to the "horse race problem", though here applied to golf          #                                       #
#                                                                                                      #
########################################################################################################


# There are three entrants in a golf tournament. They play four rounds of golf and each round is independent of the last.
# The standard deviation of their scores for one round is roughly eight shots. The market prices, expressed as
# Australian style dividends, are 5.4, 2.7 and 1.8 respectively corresponding, after normalization, to risk neutral
# probabilities of winning equal to 1 in 6, 1 in 3 and 1 in 2 respectively.
dividends = [6.0, 3.0, 2.0]
raw_dividends = [0.9 * div for div in dividends]

# These risk-neutral probabilities are consistent with ability offsets computed as follows
from pysport.golf.calibration import dividend_implied_golf_ability
ability  = dividend_implied_golf_ability( dividends = raw_dividends )
print "Relative abilities are " + str( ability )

# We can check that this model for golf scores does indeed correspond, quite closely, to the provided risk-neutral probabilities
from pysport.golf.calibration import golf_ability_implied_dividends
impl_dividends = golf_ability_implied_dividends( ability=ability )

print zip( dividends, impl_dividends )

