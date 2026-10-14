import unittest
from unittest import mock

import pandas as pd

from src import ingest

CSV = b"""series_type,date,ron95,ron97,diesel,diesel_eastmsia,ron95_budi95,ron95_skps,diesel_skds,diesel_budi
level,2026-10-08,4.67,5.10,5.27,2.15,1.99,,,2.1
change_weekly,2026-10-08,0.15,0.05,0.00,0.00,0.00,,,0.0
level,2026-06-25,3.47,4.20,4.07,2.15,1.99,,,
level,not-a-date,3.00,4.00,4.00,2.15,1.99,,,
level,2026-07-01,3.37,4.10,3.97,2.15,1.99,,,2.1
"""


def fake_session(content: bytes = CSV, error: Exception = None) -> mock.Mock:
    session = mock.Mock()
    if error:
        session.get.side_effect = error
    else:
        session.get.return_value.content = content
    return session


class LoadFuelDataTest(unittest.TestCase):
    def load(self, **kwargs) -> pd.DataFrame:
        with mock.patch.object(ingest, "get_robust_session", return_value=fake_session(**kwargs)):
            return ingest.load_fuel_data()

    def test_keeps_only_level_rows_with_valid_dates_sorted(self):
        df = self.load()
        self.assertEqual(
            df["date"].dt.strftime("%Y-%m-%d").tolist(),
            ["2026-06-25", "2026-07-01", "2026-10-08"],
        )
        self.assertTrue((df["series_type"] == "level").all())

    def test_price_columns_are_numeric(self):
        df = self.load()
        for col in ingest.PRICE_COLS:
            self.assertTrue(pd.api.types.is_float_dtype(df[col]), col)
        self.assertTrue(pd.isna(df.loc[0, "diesel_budi"]))

    def test_missing_required_column_raises(self):
        with self.assertRaises(KeyError):
            self.load(content=b"series_type,date,ron95\nlevel,2026-10-08,4.67\n")

    def test_fetch_failure_raises_runtime_error(self):
        with self.assertRaises(RuntimeError):
            self.load(error=ConnectionError("down"))


class CalculateSpreadsTest(unittest.TestCase):
    def test_spread_is_market_minus_cap(self):
        df = pd.DataFrame(
            {"ron95": [4.67], "ron95_budi95": [1.99], "diesel": [5.27], "diesel_budi": [2.10]}
        )
        out = ingest.calculate_spreads(df)
        self.assertAlmostEqual(out.loc[0, "ron95_subsidy_delta"], 2.68)
        self.assertAlmostEqual(out.loc[0, "diesel_subsidy_delta"], 3.17)

    def test_negative_spread_clips_to_zero(self):
        df = pd.DataFrame({"ron95": [1.50], "ron95_budi95": [1.99]})
        out = ingest.calculate_spreads(df)
        self.assertEqual(out.loc[0, "ron95_subsidy_delta"], 0.0)

    def test_missing_cap_leaves_spread_empty(self):
        df = pd.DataFrame({"diesel": [4.07], "diesel_budi": [float("nan")]})
        out = ingest.calculate_spreads(df)
        self.assertTrue(pd.isna(out.loc[0, "diesel_subsidy_delta"]))

    def test_skips_spread_when_cap_column_absent(self):
        out = ingest.calculate_spreads(pd.DataFrame({"diesel": [4.07]}))
        self.assertNotIn("diesel_subsidy_delta", out.columns)


if __name__ == "__main__":
    unittest.main()
