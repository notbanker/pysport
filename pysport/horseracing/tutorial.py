########################################################################################################
#                                                                                                      #
#   The module provides one solution to the "horse race problem"                                       #
#                                                                                                      #
#   We invert the relationship between win probabilities and performance densities in a competition    #
#   where all contestants' scoring distributions share the same density up to translation.             #
#                                                                                                      #
#   See the upcoming book "Risk Neutral Probability in Sport" by yours truly                           #
#                                                                                                      #
########################################################################################################

# There are three horses in a race.
# The standard deviation of their times is, we shall imagine, one second.
# The market prices, expressed as Australian style dividends, are

from pysport.horseracing.lattice_calibration import normalize_dividends
tote_dividends       = [ 17.0, 3.4, 17.0, 4.5, 8.0 ]
normalized_dividends = normalize_dividends( tote_dividends )

# These risk-neutral probabilities are consistent with ability offsets computed as follows
from pysport.horseracing.lattice_calibration import dividend_implied_racing_ability
ability  = dividend_implied_racing_ability( dividends = tote_dividends)
print "Relative abilities are " + str( ability )

# We can check that this inversion is indeed accurate to around three or four significant figures
from pysport.horseracing.lattice_calibration import racing_ability_implied_dividends
impl_dividends = racing_ability_implied_dividends( ability=ability )

print zip(normalized_dividends, impl_dividends)

