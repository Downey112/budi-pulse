import math
import os
import unittest
from unittest import mock

import pandas as pd

from src import db


def spreads_frame(n: int = 2) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-10-01", periods=n, freq="7D"),
            "ron95": [4.52] * n,
            "ron95_budi95": [1.99] * n,
            "ron95_subsidy_delta": [2.53] * n,
            "diesel": [5.27] * n,
            "diesel_budi": [2.10] * n,
            "diesel_subsidy_delta": [3.17] * n,
        }
    )


class CleanValueTest(unittest.TestCase):
    def test_rounds_to_four_places(self):
        self.assertEqual(db.clean_value(2.123456), 2.1235)

    def test_missing_and_infinite_become_none(self):
        for val in (None, float("nan"), pd.NA, math.inf, -math.inf):
            self.assertIsNone(db.clean_value(val), val)


class SerializeRecordsTest(unittest.TestCase):
    def test_maps_columns_to_table_schema(self):
        records = db.serialize_records(spreads_frame(1))
        self.assertEqual(
            records,
            [
                {
                    "date": "2026-10-01",
                    "ron95_market": 4.52,
                    "ron95_budi": 1.99,
                    "ron95_gap": 2.53,
                    "diesel_market": 5.27,
                    "diesel_budi": 2.10,
                    "diesel_gap": 3.17,
                }
            ],
        )

    def test_nan_and_missing_columns_become_none(self):
        df = spreads_frame(1).drop(columns=["diesel_budi", "diesel_subsidy_delta"])
        df["ron95"] = float("nan")
        record = db.serialize_records(df)[0]
        self.assertIsNone(record["ron95_market"])
        self.assertIsNone(record["diesel_budi"])
        self.assertIsNone(record["diesel_gap"])

    def test_empty_frame_gives_no_records(self):
        self.assertEqual(db.serialize_records(spreads_frame(0)), [])


class UploadToSupabaseTest(unittest.TestCase):
    def upload(self, spreads: pd.DataFrame) -> tuple:
        client = mock.Mock()
        with mock.patch.object(db, "load_fuel_data"), mock.patch.object(
            db, "calculate_spreads", return_value=spreads
        ), mock.patch("builtins.print"):
            count = db.upload_to_supabase(client)
        return count, client.table.return_value.upsert

    def test_upserts_on_date_in_batches(self):
        count, upsert = self.upload(spreads_frame(db.BATCH_SIZE + 3))
        self.assertEqual(count, db.BATCH_SIZE + 3)
        self.assertEqual([len(c.args[0]) for c in upsert.call_args_list], [db.BATCH_SIZE, 3])
        for call in upsert.call_args_list:
            self.assertEqual(call.kwargs, {"on_conflict": "date"})

    def test_no_records_skips_upsert(self):
        count, upsert = self.upload(spreads_frame(0))
        self.assertEqual(count, 0)
        upsert.assert_not_called()


class SupabaseClientTest(unittest.TestCase):
    def test_missing_credentials_raise(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                db.get_supabase_client()


if __name__ == "__main__":
    unittest.main()
