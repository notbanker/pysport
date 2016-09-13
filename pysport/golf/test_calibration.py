from unittest import TestCase, main
from .calibration import dividend_implied_golf_ability, golf_ability_implied_dividends, GOLF_L, GOLF_UNIT

class ModuleTests( TestCase ):

    def setUp(self):
        self.unit = GOLF_UNIT
        self.L    = GOLF_L

    def test_calibration( self ):
        dividends               = [ 6.0, 3.0, 2.0 ]
        ability                 = dividend_implied_golf_ability( dividends= dividends )
        print ability
        prices                  = golf_ability_implied_dividends( ability )
        print prices


if __name__ == '__main__':
    main()