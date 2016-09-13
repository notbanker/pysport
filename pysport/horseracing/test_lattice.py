from unittest import TestCase, main
from .lattice import skew_normal_density, mean_of_density, densitiesPlot, winner_of_many, implicit_state_prices,\
    sample_winner_of_many, densities_from_offsets, state_prices_from_offsets
from .lattice_calibration import implied_ability

PLOTS=False

class ModuleTests( TestCase ):

    def setUp(self):
        self.unit = 0.1
        self.L    = 150

    def test_plot_skew( self ):
        skew = skew_normal_density(L=self.L, unit = self.unit, a=1.5)
        print "mean is " + str(mean_of_density(skew, unit=self.unit))
        if PLOTS:
            densitiesPlot( [skew], unit=self.unit )

    def test_minimumPdf(self):
        skew1 = skew_normal_density(L=self.L, unit = self.unit, a=1.5)
        skew2 = skew_normal_density(L=self.L, unit = self.unit, a=1.5, loc = -0.5)
        skew3 = skew_normal_density(L=self.L, unit = self.unit, a=1.5, loc = -1.0)
        best, multiplicity  = winner_of_many([skew1, skew2, skew3])
        if PLOTS:
            densitiesPlot( [ skew1/self.unit, skew2/self.unit, skew3/self.unit, best /self.unit, multiplicity ], self.unit, legend=['1','2,','3','best', 'multiplicity'] )

    def test_minimumPdfMany( self ):
        densities = [skew_normal_density(L= self.L, unit=self.unit, a =0.1 * i) for i in xrange(150)]
        best, multiplicity      = winner_of_many(densities)
        if PLOTS:
            densitiesPlot( [ d/self.unit for d in densities[:5] ]  + [ best/self.unit, multiplicity ], self.unit )

    def test_implicit_payoffs( self ):
        skew1 = skew_normal_density(L=self.L, unit = self.unit, a=1.5)
        skew2 = skew_normal_density(L=self.L, unit = self.unit, a=1.5, loc = -0.5)
        skew3 = skew_normal_density(L=self.L, unit = self.unit, a=1.5, loc = -1.0)
        densityAll, multiplicityAll  = winner_of_many([skew1, skew2, skew3])
        payoffs = implicit_state_prices( density=skew1, densityAll=densityAll, multiplicityAll = multiplicityAll, cdf = None, cdfAll = None, offsets = None )

        if PLOTS:
            import matplotlib.pyplot as plt
            plt.plot( payoffs )
            plt.show()

    def test_monte_carlo( self ):
        skew1     = skew_normal_density(L=25, unit = self.unit, a=1.5)
        densities = [ skew1, skew1, skew1 ]
        densityAll, multiplicityAll  = winner_of_many(densities)
        densityAllCheck = sample_winner_of_many(densities, nSamples = 5000)
        if PLOTS:
            densitiesPlot( [ densityAll, densityAllCheck ], unit = 0.1 )

    def test_calibration( self ):
        skew1                   = skew_normal_density(L=self.L, unit = self.unit, a=1.5)
        prices                  = [ 0.2, 0.3, 0.5 ]
        implied_offsets         = implied_ability(prices = prices, density = skew1, nIter = 2)
        inferred_prices         = state_prices_from_offsets( skew1, implied_offsets )
        print str(inferred_prices)
        densities               = densities_from_offsets( skew1, implied_offsets )
        densityAllAgain, multiplicityAll  = winner_of_many(densities)
        if PLOTS:
            densitiesPlot( [ densityAllAgain ] + densities, unit = 0.1, legend = ['guess','analytic','1','2','3'] )

    def test_calibration_long( self ):
        density                 = skew_normal_density(L=500, unit = self.unit, a=1.5)
        n                       = 150
        true_offsets            = [ k for k in xrange( n ) ]
        state_prices            = state_prices_from_offsets( density=density, offsets=true_offsets )
        print "State prices are " + str( state_prices )
        offset_samples          = list( xrange( -100, 100 ))[::-1]
        # Now try to infer offsets from state prices
        implied_offsets         = implied_ability( prices = state_prices, density = density, offset_samples= offset_samples)
        densities               = densities_from_offsets( density, implied_offsets )
        densityAllAgain, multiplicityAll  = winner_of_many(densities)
        if PLOTS:
            densitiesPlot( [ densityAllAgain ] + densities[:3] + [ densities[-1] ], unit = 0.1, legend = ['best','1','2','3','last'] )
            import matplotlib.pyplot as plt
            plt.scatter( true_offsets, [ io - implied_offsets[0] for io in implied_offsets ] )
            plt.xlabel('True offset increments')
            plt.ylabel('Implied offset increments')
            plt.show()

