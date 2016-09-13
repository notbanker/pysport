from .lattice import skew_normal_density, center_density,\
    state_prices_from_offsets, densities_and_coefs_from_offsets, winner_of_many,\
    expected_payoff, densities_from_offsets, implicit_state_prices, densitiesPlot
import pandas as pd  # todo: get rid of this dependency
import numpy as np

def dividend_implied_racing_ability( dividends ):
    return dividend_implied_ability( dividends=dividends, density=racing_density( loc=0.0 ) )

def racing_ability_implied_dividends( ability ):
    return ability_implied_dividends( ability, density=racing_density( loc=0.0 )   )


RACING_L     = 500
RACING_UNIT  = 0.1
RACING_SCALE = 1.0
RACING_A     = 1.0

def make_nan_2000( x ) :
    """ Longshots """
    if pd.isnull( x ):
        return 2000.
    else:
        return x

def normalize( p ):
    """ Naive renormalization of probabilities """
    S = sum( p )
    return [ pr/S for pr in p ]

def prices_from_dividends( dividends ):
    """ Risk neutral probabilities using naive renormalization """
    return normalize( [ 1. / make_nan_2000(x) for x in dividends ] )

def dividends_from_prices( prices ):
    """ Australian style dividends """
    return [ 1./d for d in normalize( prices ) ]

def normalize_dividends( dividends ):
    return dividends_from_prices( prices_from_dividends( dividends ))


def racing_density( loc ):
    """ A rough and ready distribution of performance distributions for one round """
    density = skew_normal_density( L=RACING_L, unit=RACING_UNIT, loc=0, scale=RACING_SCALE, a=RACING_A )
    return center_density( density )

def dividend_implied_ability( dividends, density ):
    """ Infer risk-neutral implied_ability from Australian style dividends

    :param dividends:    [ 7.6, 12.0, ... ]
    :return: [ float ]   Implied ability

    """
    state_prices            = prices_from_dividends( dividends )
    implied_offsets_guess   = [ 0 for _ in state_prices]
    L                       = len( density )/2
    offset_samples          = list( xrange( -L/4, L/4 ))[::-1]
    ability                 = implied_ability( prices = state_prices, density = density, \
                                               offset_samples = offset_samples, implied_offsets_guess = implied_offsets_guess, nIter = 3)
    return ability

def ability_implied_dividends( ability, density ):
    """ Return betfair style prices
    :param ability:
    :return: [ 7.6, 12.3, ... ]
    """
    state_prices = state_prices_from_offsets( density=density, offsets = ability)
    return [ 1./sp for sp in state_prices ]

def implied_ability( prices, density, offset_samples = None, implied_offsets_guess = None, nIter = 3, verbose = False, visualize = False):
    """ Finds location translations of a fixed density so as to replicate given state prices for winning """

    L = len( density )
    if offset_samples is None:
        offset_samples = list( xrange( -L/4, L/4 ))[::-1]     # offset_samples should be descending TODO: add check for this
    else:
        _assert_descending( offset_samples )

    if implied_offsets_guess is None:
        implied_offsets_guess = range( len(prices) )

    # First guess at densities
    densities, coefs                      = densities_and_coefs_from_offsets( density, implied_offsets_guess )
    densityAllGuess, multiplicityAllGuess = winner_of_many( densities )
    densityAll                            = densityAllGuess.copy()
    multiplicityAll                       = multiplicityAllGuess.copy()
    guess_prices = [ np.sum( expected_payoff( density, densityAll, multiplicityAll, cdf = None, cdfAll = None)) for density in densities]

    for _ in xrange( nIter ):
        if visualize:
            # temporary hack to check progress of optimization
            densitiesPlot( [ densityAll] + densities , unit=0.1 )
        implied_prices              = implicit_state_prices( density=density, densityAll=densityAll, multiplicityAll = multiplicityAll, offsets=offset_samples )
        implied_offsets             = np.interp( prices, implied_prices, offset_samples )
        densities                   = densities_from_offsets( density, implied_offsets )
        densityAll, multiplicityAll = winner_of_many( densities )
        guess_prices = [ np.sum(expected_payoff(density, densityAll, multiplicityAll, cdf = None, cdfAll = None)) for density in densities ]
        approx_prices  = [ np.round( pri, 3 ) for pri in prices]
        approx_guesses = [ np.round( pri, 3 ) for pri in guess_prices]
        if verbose:
            print zip( approx_prices,  approx_guesses )[:5]

    return implied_offsets


def _assert_descending( xs ):
    for d in np.diff( xs ):
        if d>0:
            raise ValueError("Not descending")