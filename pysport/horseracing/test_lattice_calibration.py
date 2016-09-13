from unittest import TestCase, main
from ..horseracing.lattice_calibration import dividend_implied_racing_ability, racing_ability_implied_dividends
class ModuleTests( TestCase ):

    def setUp(self):
        self.unit = 0.1
        self.L    = 500

    def test_calibration( self ):
        dividends               = [ 6.0, 3.0, 2.0 ]
        ability                 = dividend_implied_racing_ability( dividends= dividends )
        print ability
        prices                  = racing_ability_implied_dividends( ability )
        print prices


if __name__ == '__main__':
    main()