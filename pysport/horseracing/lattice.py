from scipy import linspace
from scipy.stats import norm
import numpy as np
import math

def densitiesPlot( densities, unit, legend = None ):
    import matplotlib.pyplot as plt
    L = len( densities[0] )/2
    pts = symmetric_lattice( L=L, unit=unit )
    for density in densities:
        plt.plot( pts, density )
    if legend is not None:
        plt.legend( legend )
    plt.grid()
    plt.show()


def integer_shift( cdf, k ):
    """ Shift cdf to the *right* so it represents the cdf for Y ~ X + k*unit
    :param cdf:
    :param k:     int    Number of lattice points
    :return:
    """
    if k < 0:
        return np.append( cdf[ abs(k):], cdf[-1]*np.ones( abs(k) ) )
    elif k==0:
        return cdf
    else:
        return np.append( np.zeros(k), cdf[:-k] )

def fractional_shift( cdf, x ):
    """ Shift cdf to the *right* so it represents the cdf for Y ~ X + x*unit
    :param cdf:
    :param x:     float    Number of lattice points to shift (need not be integer)
    :return:
    """
    ( l, lc), ( u, uc) = _low_high( x )
    return  lc * integer_shift( cdf, l ) + uc * integer_shift( cdf, u )

def _low_high( offset ):
    l = math.floor( offset )
    u = math.ceil( offset )
    r = offset - l
    return (l, 1-r ), (u, r)

def fractional_shift_density( density, x ):
    """ Shift pdf to the *right* so it represents the pdf for Y ~ X + x*unit """
    cdf                = pdf_to_cdf(density)
    shifted_cdf        = fractional_shift( cdf, x )
    return  cdf_to_pdf(shifted_cdf)
    return shifted_pdf

def center_density( density ):
    """ Shift density to near its mean """
    m = mean_of_density(density, unit=1.0)
    return fractional_shift_density( density, -m )

def mean_of_density( density, unit ):
    L   = len( density) /2
    pts = symmetric_lattice( L=L, unit=unit )
    return np.inner( density, pts )

def symmetric_lattice(L, unit):
    return unit*linspace( -L, L, 2*L+1 )

#############################################
#   Simple family of skewed distributions   #
#############################################

def skew_normal_density( L, unit, loc=0, scale=1.0, a=2.0):
    """ Skew normal as a lattice density """
    lattice = symmetric_lattice(L=L, unit=unit)
    density = np.array( [ _unnormalized_skew_cdf(x, loc=loc, scale=scale, a=a ) for x in lattice])
    density = density / np.sum( density )
    return density

def _unnormalized_skew_cdf(x, loc=0, scale=1, a=2.0):
    """ Proportional to skew-normal density
    :param x:
    :param loc:    location
    :param scale:  scale
    :param a:      controls skew (a>0 means fat tail on right)
    :return:  np.array length 2*L+1
    """
    t = (x-loc) / scale
    return 2 / scale * norm.pdf(t) * norm.cdf(a*t)

# Probabilities on lattices
# Nothing below here depends on the unit chosen

#############################################
#  Order statistics on lattices             #
#############################################

def pdf_to_cdf( density ):
    """  Prob( X <= k*unit )    """
    return np.cumsum( density )

def cdf_to_pdf(cumulative):
    """ Given cumulative distribution on lattice, return the pdf """
    prepended = np.insert( cumulative, 0, 0.)
    return np.diff( prepended )

def winner_of_many( densities, multiplicities = None):
    """ The PDF of the minimum of the random variables represented by densities
    :param   densities:  [ np.array   ]
    :return: np.array
    """
    d  = densities[0]
    multiplicities = multiplicities or [ None for _ in densities ]
    m = multiplicities[0]
    for d2, m2 in zip( densities[1:], multiplicities[1:] ):
        d, m = _winner_of_two_pdf( d, d2, multiplicityA=m, multiplicityB = m2 )
    return d, m

def sample_from_cdf( cdf, nSamples ):
    """ Monte Carlo sample """
    rvs = np.random.rand( nSamples )
    return [ sum( [ rv>c for c in cdf ] ) for rv in rvs ]

def sample_winner_of_many( densities, nSamples = 5000 ):
    """ The PDF of the minimum of the integer random variables represented by densities, by Monte Carlo """
    cdfs = [pdf_to_cdf(density) for density in densities]
    cols = [sample_from_cdf(cdf, nSamples) for cdf in cdfs]
    rows = map( list, zip( *cols ))
    D    = [ min( row ) for row in rows ]
    density = np.bincount( D, minlength=len( densities[0] ) ) / (1.0*nSamples)
    return density

def expected_payoff( density, densityAll, multiplicityAll, cdf = None, cdfAll = None):
    """ Returns expected _conditional_payoff_against_rest broken down by score,
       where _conditional_payoff_against_rest is 1 if we are better than rest (lower) and 1/(1+multiplicity) if we are equal

    """
    # Use np.sum( expected_payoff ) for the expectation
    if cdf is None:
        cdf      = pdf_to_cdf(density)
    if cdfAll is None:
        cdfAll   = pdf_to_cdf(densityAll)
    if density is None:
        density = cdf_to_pdf(cdf)
    if densityAll is None:
        densityAll = cdf_to_pdf(cdfAll)
    S       = 1 - cdfAll
    S1      = 1 - cdf
    Srest   = ( S + 1e-18 ) / ( S1 + 1e-6 )
    cdfRest = 1 - Srest

    # Multiplicity inversion (uses notation from blog post)
    # This is written up in my blog post
    m       = multiplicityAll
    f1      = density
    m1      = 1.0
    fRest   = cdf_to_pdf(cdfRest)
                                              # numer = m*f1*Srest + m*(f1+S1)*fRest - m1*f1*( Srest + fRest )
                                              # denom = fRest*(f1+S1)
    numer   = m*f1*Srest + m*(f1+S1)*fRest - m1*f1*( Srest + fRest )
    denom   = fRest*(f1+S1)
    multiplicityLeftTail = (1e-18 + numer ) / ( 1e-18 + denom )
    multiplicityRest = multiplicityLeftTail

    T1      = (S1 +1.0e-18) / (f1 + 1e-6 )      # This calculation is more stable on the right tail. It should tend to zero eventually
    Trest   = (Srest + 1e-18) / ( fRest + 1e-6 )
    multiplicityRightTail = m*Trest / (1 + T1) + m - m1 * (1 + Trest ) / (1 + T1 )

    k       = list( f1 == max(f1) ).index( True )
    multiplicityRest[k:] = multiplicityRightTail[k:]

    return _conditional_payoff_against_rest(density = density, densityRest = None, multiplicityRest = multiplicityRest, cdf = cdf, cdfRest = cdfRest)

def _winner_of_two_pdf( densityA, densityB, multiplicityA = None, multiplicityB = None, cdfA = None, cdfB = None):
    """ The PDF of the minimum of two random variables represented by densities
    :param   densityA:   np.array
    :param   densityB:   np.array
    :return: density, multiplicity
    """
    cdfA    = pdf_to_cdf(densityA)
    cdfB    = pdf_to_cdf(densityB)
    cdfMin  = 1 - np.multiply( 1 - cdfA, 1- cdfB )
    density = cdf_to_pdf(cdfMin)
    L       = len( density ) / 2
    if multiplicityA is None:
        multiplicityA = np.ones( 2*L+1 )
    if multiplicityB is None:
        multiplicityB = np.ones( 2*L+1 )

    winA, draw, winB = _conditional_win_draw_loss( densityA, densityB, cdfA, cdfB )
    multiplicity  = ( winA*multiplicityA + draw*(multiplicityA+multiplicityB) + winB*multiplicityB +1e-18) / ( winA+draw+winB+1e-18)
    return density, multiplicity

def _conditional_win_draw_loss(densityA, densityB, cdfA, cdfB):
    """ Conditional win, draw and loss probability lattices for a two horse race """
    win   = densityA * ( 1 - cdfB )
    draw  = densityA * densityB
    lose  = densityB * ( 1 - cdfA )
    return win, draw, lose

def _conditional_payoff_against_rest(density, densityRest, multiplicityRest, cdf = None, cdfRest = None):
    """ Returns expected _conditional_payoff_against_rest broken down by score, where _conditional_payoff_against_rest is 1 if we are better than rest (lower) and 1/(1+multiplicity) if we are equal """
    # use np.sum( _conditional_payoff_against_rest) for the expectation
    if cdf is None:
        cdf = pdf_to_cdf(density)
    if cdfRest is None:
        cdfRest = pdf_to_cdf(densityRest)
    if density is None:
        density = cdf_to_pdf(cdf)
    if densityRest is None:
        densityRest = cdf_to_pdf(cdfRest)

    win, draw, loss = _conditional_win_draw_loss(density, densityRest, cdf, cdfRest)
    return win + draw / (1+multiplicityRest )

def densities_and_coefs_from_offsets( density, offsets ):
    """ Given a density and a list of offsets (which might be non-integer)
    :param density:  np.ndarray
    :param offsets: [ float ]
    :return: [ np.ndarray ]
    """
    cdf             = pdf_to_cdf(density)
    coefs           = [ _low_high( offset ) for offset in offsets ]
    cdfs            = [lc * integer_shift(cdf, l) + uc * integer_shift(cdf, u) for (l, lc), (u, uc) in coefs]
    return [cdf_to_pdf(cdf) for cdf in cdfs], coefs

def densities_from_offsets( density, offsets ):
    return densities_and_coefs_from_offsets( density, offsets)[0]

def state_prices_from_offsets( density, offsets ):
    densities = densities_from_offsets( density, offsets )
    densityAll, multiplicityAll = winner_of_many( densities )
    return implicit_state_prices( density, densityAll = densityAll, multiplicityAll=multiplicityAll, offsets=offsets )

def implicit_state_prices( density, densityAll, multiplicityAll = None, cdf = None, cdfAll = None, offsets = None ):
    """ Returns the expected _conditional_payoff_against_rest as a function of location changes in cdf """
    L = len( density )/2
    if cdf is None:
        cdf = pdf_to_cdf( density )
    if cdfAll is None:
        cdfAll = pdf_to_cdf(densityAll)
    if multiplicityAll is None:
        multiplicityAll = np.ones( 2*L+1 )
    if offsets is None:
        offsets = xrange( -L/2, L/2 )
    implicit = list()
    for k in offsets:
        if k==int( k ):
            offset_cdf = integer_shift( cdf, k )
            ip         = expected_payoff( density = None, densityAll = densityAll, multiplicityAll=multiplicityAll, cdf = offset_cdf, cdfAll = cdfAll)
            implicit.append( np.sum( ip ) )
        else:
            (l, l_coef ), ( r, r_coef) = _low_high( k )
            offset_cdf_left            = integer_shift(cdf, l)
            offset_cdf_right           = integer_shift(cdf, r)
            ip_left   = expected_payoff(density = None, densityAll = densityAll, multiplicityAll=multiplicityAll, cdf = offset_cdf_left, cdfAll = cdfAll)
            ip_right  = expected_payoff(density = None, densityAll = densityAll, multiplicityAll=multiplicityAll, cdf = offset_cdf_right, cdfAll = cdfAll)
            implicit.append( l_coef*np.sum( ip_left ) + r_coef*np.sum( ip_right ) )

    return implicit




