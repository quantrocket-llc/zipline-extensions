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

import io
import zipline
import pandas as pd
from quantrocket.history import get_db_config, download_history_file
from quantrocket.master import download_master_file
from zipline_extensions.errors import BadIngestionArgument

# (for minutely bundles) minutes_per_day must be passed to the
# register function. Look these up per calendar in
# zipline.utils.calendars.exchange_calendar_*
MINUTES_PER_DAY_PER_EXCHANGE = {
    "NYSE": 6.5*60, # 9:30AM-4PM
    "us_futures": 24*60, # 6PM-6PM
    "CME": 24*60, # 5PM-5PM
    "CFE": 6.75 * 60, # 8:30AM-3:15PM
    "ICE": 22*60, # 8PM-6PM
    "BMF": 6*60, # 10AM-4PM
    "LSE": 8.5*60, # 8AM-4:30PM
    "TSX": 6.5*6, # 9:30AM-4PM
}

class QuantRocketHistoryBundler(object):

    def __init__(self, code, calendar=None, logger=None):
        self.code = code
        self.calendar_name = calendar or "NYSE"
        self.db_config = None
        self.bar_size = None
        self.universes = None
        self.logger = logger

    def validate_config(self):
        """
        Gets the db config and validates it.
        """
        self.db_config = get_db_config(self.code)
        self.bar_size = self.db_config.get("bar_size", None)

        if self.bar_size not in ("1 min", "1 day"):
            raise BadIngestionArgument(
                "Zipline requires 1 minute or 1 day bars, but {0} has {1} bars".format(
                self.code, self.bar_size)
            )

        self.universes = self.db_config.get("universes", None)

        if not self.universes:
            raise BadIngestionArgument(
                "1 or more universes is required but {0} defines none".format(self.code))

    def build_and_register(self):
        """
        Builds and registers a bundle ingestion function.
        """

        self.validate_config()

        def quantrocket_history_bundle(
            environ,
            asset_db_writer,
            minute_bar_writer,
            daily_bar_writer,
            adjustment_writer,
            calendar,
            start_session,
            end_session,
            cache,
            show_progress,
            output_dir):

            f = io.StringIO()
            download_history_file(self.code, f, fields=["Open","Close","High","Low","Volume"])
            prices = pd.read_csv(f, index_col=["Date","ConId"],parse_dates=["Date"])

            self._write_assets(prices, asset_db_writer)

            if self.bar_size == "1 day":
                self._write_daily_bars(prices, daily_bar_writer)
            else:
                self._write_minute_bars(prices, minute_bar_writer)

            # Call this so tables get created, otherwise zipline fails
            adjustment_writer.write()

        minutes_per_day = MINUTES_PER_DAY_PER_EXCHANGE[self.calendar_name]
        minutes_per_day = int(minutes_per_day)

        zipline.data.bundles.register(
            self.code, quantrocket_history_bundle, calendar_name=self.calendar_name,
            minutes_per_day=minutes_per_day)

    def _write_assets(self, prices, asset_db_writer):
        """
        Queries the master service and prepares the securities for the asset
        writer.
        """

        f = io.StringIO()

        download_master_file(
            f, universes=self.universes,
            delisted=True, fields=["ConId", "PrimaryExchange", "Symbol", "SecType",
                                   "LocalSymbol", "LongName", "MinTick",
                                   "Multiplier", "LastTradeDate", "ContractMonth",
                                   "Timezone", "UnderConId"])

        assets = pd.read_csv(f, index_col="ConId")
        assets[["Symbol", "LocalSymbol"]] = assets[["Symbol", "LocalSymbol"]].astype(str)

        grouped_by_conid = prices.reset_index().groupby("ConId")
        max_dates = grouped_by_conid.Date.max()
        min_dates = grouped_by_conid.Date.min()
        min_dates.name = "start_date"
        max_dates.name = "end_date"
        assets = assets.join(min_dates).join(max_dates)
        assets["first_traded"] = assets["start_date"]

        exchanges = pd.DataFrame(
            assets, columns=["PrimaryExchange","Timezone"]).drop_duplicates()
        exchanges = exchanges.rename(columns={
            "PrimaryExchange": "exchange",
            "Timezone": "timezone"
            })

        equities = assets[assets.SecType == "STK"].copy()
        if equities.empty:
            equities = None
        else:
            equities = pd.DataFrame(equities, columns=["PrimaryExchange", "Symbol", "LongName", "start_date", "end_date", "first_traded"])
            equities = equities.rename(columns={
                "PrimaryExchange": "exchange",
                "Symbol": "symbol",
                "LongName": "asset_name"
            })

        futures = assets[assets.SecType == "FUT"].copy()
        if futures.empty:
            futures = None
            root_symbols = None
        else:
            # Concat local symbol plus contract month to ensure unique symbol
            futures["symbol"] = futures.LocalSymbol.str.cat(
                futures.ContractMonth.astype(str), "-")

            futures = futures.rename(columns={
                "PrimaryExchange": "exchange",
                "Symbol": "root_symbol",
                "LongName": "asset_name",
                "Multiplier": "multiplier",
                "MinTick": "tick_size",
                "LastTradeDate": "auto_close_date",
                "UnderConId": "root_symbol_id"
            })
            futures["expiration_date"] = futures.auto_close_date
            root_symbols = pd.DataFrame(
                futures, columns=["root_symbol", "exchange", "root_symbol_id"]).drop_duplicates()
            futures = futures.drop(["root_symbol_id", "LocalSymbol", "ContractMonth", "SecType"], axis=1)

        asset_db_writer.write(
                equities=equities,
                futures=futures,
                exchanges=exchanges,
                root_symbols=root_symbols)

    def _write_minute_bars(self, prices, minute_bar_writer):
        """
        Queries history and passes it to minute bar writer.
        """
        panel = prices.to_panel().swapaxes("items","minor").rename(minor={
            "Volume": "volume",
            "Open": "open",
            "Close": "close",
            "High": "high",
            "Low": "low"
        })

        minute_bar_writer.write(panel.iteritems(), show_progress=True)

    def _write_daily_bars(self, prices, daily_bar_writer):
        """
        Queries history and passes it to daily bar writer.
        """
        panel = prices.to_panel().swapaxes("items","minor").rename(minor={
            "Volume": "volume",
            "Open": "open",
            "Close": "close",
            "High": "high",
            "Low": "low"
        })

        panel = self._reindex_panel_for_mismatched_sessions(panel, daily_bar_writer)
        daily_bar_writer.write(panel.iteritems(), assets=set(panel.items), show_progress=True)

    def _reindex_panel_for_mismatched_sessions(self, panel, daily_bar_writer):

        """
        Zipline will fail if the date index doesn't perfectly align with the
        expected calendar session, but let's just warn. We also ffill missing
        data as all-null dates can cause errors (e.g. in Pipeline).

        See zipline.data.us_equity_pricing.BcolzDailyBarWriter._write_internal

        """
        sessions = daily_bar_writer._calendar.sessions_in_range(
            daily_bar_writer._start_session, daily_bar_writer._end_session
        )
        asset_first_day = panel.major_axis.min()
        asset_last_day = panel.major_axis.max()
        asset_sessions = sessions[
            sessions.slice_indexer(asset_first_day, asset_last_day)
        ]

        # Same length, so we're fine
        if len(asset_sessions) == len(panel.major_axis):
            return panel

        missing = asset_sessions.difference(
            pd.to_datetime(
                panel.major_axis.values,
                unit='s',
                utc=True,
            )).tolist()

        extra = pd.to_datetime(
            panel.major_axis.values,
            unit='s',
            utc=True,
            ).difference(asset_sessions).tolist()

        missing_dates_msg = extra_dates_msg = ""

        if missing:
            missing_dates_msg = "missing sessions: {0}".format(
                ", ".join([ts.isoformat() for ts in missing[:20]]))
            if len(missing) > 20:
                missing_dates_msg += " and {0} more".format(len(missing) - 20)

        if extra:
            extra_dates_msg = "extra sessions: {0}".format(
                ", ".join([ts.isoformat() for ts in extra[:20]]))
            if len(extra) > 20:
                extra_dates_msg += " and {0} more".format(len(extra) - 20)

        base_msg = "{0} calendar and {1} history do not align so re-indexing history to calendar".format(
                   self.calendar_name, self.code)

        msg = "; ".join([msg_part for msg_part in (base_msg, missing_dates_msg, extra_dates_msg) if msg_part])
        if self.logger:
            self.logger.warning(msg)

        panel = panel.reindex(major_axis=pd.to_datetime(asset_sessions.values))

        panel = self.fillna_panel(panel)

        return panel

    @classmethod
    def fillna_panel(cls, panel):
        """
        Fills NaNs in the panel as follows:

        - nan volume becomes 0
        - close is forward-filled
        - open, high, low are forward-filled with the prior close

        Before:
                     open  high   low close volume
        2018-02-06  50.10 51.00 49.90 50.56  45100
        2018-02-07    NaN   NaN   NaN   NaN    NaN
        2018-02-08  48.89 48.99 46.58 47.20  90500

        After:
                     open  high   low close volume
        2018-02-06  50.10 51.00 49.90 50.56  45100
        2018-02-07  50.56 50.56 50.56 50.56      0
        2018-02-08  48.89 48.99 46.58 47.20  90500
        """

        panel = panel.swapaxes("items","minor")

        panel.volume.fillna(0, inplace=True)
        panel.close.fillna(method="ffill", inplace=True)
        # For some reason using inplace=True on the follow doesn't preserve
        # the fill values after swapaxes below
        panel.open = panel.open.fillna(panel.close.shift())
        panel.high = panel.high.fillna(panel.close.shift())
        panel.low = panel.low.fillna(panel.close.shift())

        panel = panel.swapaxes("items","minor")

        return panel
