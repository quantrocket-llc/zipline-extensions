# Copyright 2018 QuantRocket LLC - All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# To run: python3 -m unittest discover -t . -s . -p test*.py

import unittest
import pandas as pd
import numpy as np
from zipline_extensions.data.bundles.history import QuantRocketHistoryBundler

class QuantRocketHistoryBundlerTestCase(unittest.TestCase):

    def test_fillna_panel(self):
        symbol1 = pd.DataFrame(
            dict(open=[50.10,np.nan,48.89],
                 high=[51.00,np.nan,48.99],
                 low=[49.90,np.nan,46.58],
                 close=[50.56,np.nan,47.20],
                 volume=[45100,np.nan,90500]),
            index=[pd.Timestamp("2018-02-06"),
                   pd.Timestamp("2018-02-07"),
                   pd.Timestamp("2018-02-08")])
        symbol2 = pd.DataFrame(
            dict(open=[20.10,21.89],
                 high=[21.00,22.00],
                 low=[20.05,20.50],
                 close=[20.90,21.75],
                 volume=[100500,78800]),
            index=[pd.Timestamp("2018-02-06"),
                   pd.Timestamp("2018-02-07")])
        panel = pd.Panel(data=dict(symbol1=symbol1, symbol2=symbol2))
        panel = QuantRocketHistoryBundler.fillna_panel(panel)
        self.assertEqual(
            panel.symbol1.to_dict(orient="list"),
            {'close': [50.56, 50.56, 47.2],
             'high': [51.0, 50.56, 48.99],
             'low': [49.9, 50.56, 46.58],
             'open': [50.1, 50.56, 48.89],
             'volume': [45100.0, 0.0, 90500.0]}
        )
        self.assertEqual(
            panel.symbol2.to_dict(orient="list"),
            {'close': [20.9, 21.75, 21.75],
             'high': [21.0, 22.0, 21.75],
             'low': [20.05, 20.5, 21.75],
             'open': [20.1, 21.89, 21.75],
             'volume': [100500.0, 78800.0, 0.0]}
        )
