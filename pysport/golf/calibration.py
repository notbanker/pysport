
from ..horseracing.lattice import skew_normal_density, center_density
from ..horseracing.lattice_calibration import dividend_implied_ability, ability_implied_dividends
import math

GOLF_L     = 500
GOLF_UNIT  = 0.1   # Score differential over 4 rounds is +/- 50 range
GOLF_SCALE = 2*math.sqrt( 8.37 )
GOLF_A     = 1.0

def dividend_implied_golf_ability( dividends ):
    return dividend_implied_ability( dividends=dividends, density=golf_density( loc=0.0 ) )

def golf_ability_implied_dividends( ability ):
    return ability_implied_dividends( ability, density=golf_density( loc=0.0 )   )


def golf_density( loc ):
    """ A rough and ready distribution of golf score distributions for one round """
    density = skew_normal_density( L=GOLF_L, unit=GOLF_UNIT, loc=0, scale=GOLF_SCALE, a=GOLF_A )
    return center_density( density )

