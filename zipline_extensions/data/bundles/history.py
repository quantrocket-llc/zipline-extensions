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
import requests
import pandas as pd
import threading
import queue
import logging
from functools import wraps
from quantrocket.history import get_db_config, download_history_file
from quantrocket.master import download_master_file
from zipline_extensions.errors import BadIngestionArgument, NoData
from zipline.data.resample import minute_frame_to_session_frame

logger = logging.getLogger("quantrocket.zipline")
logger.setLevel(logging.DEBUG)

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

class _BaseHistoryIngester:

    def __init__(
        self,
        code,
        start_date=None,
        end_date=None,
        universes=None,
        conids=None,
        exclude_universes=None,
        exclude_conids=None):

        self.code = code
        self.start_date = start_date
        self.end_date = end_date
        self.universes = universes
        self.conids = conids
        self.exclude_universes = exclude_universes
        self.exclude_conids = exclude_conids
        self.securities = None # DataFrame of securities
        self.min_dates = None # Series of conid: min date
        self.max_dates = None # Series of conid: max date

    def ingest(
        self,
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

        self._get_securities()

        self._write_bars(daily_bar_writer, minute_bar_writer, calendar)

        self._write_assets(asset_db_writer)

        # Call this so tables get created, otherwise zipline fails
        adjustment_writer.write()

    def _get_securities(self):
        """
        Queries the master db and gets a securities master file.
        """
        f = io.StringIO()

        download_master_file(
            f,
            universes=self.universes,
            conids=self.conids,
            exclude_universes=self.exclude_universes,
            exclude_conids=self.exclude_conids,
            delisted=True,
            fields=["ConId", "PrimaryExchange", "Symbol", "SecType",
                    "LocalSymbol", "LongName", "MinTick",
                    "Multiplier", "LastTradeDate", "ContractMonth",
                    "Timezone", "UnderConId"])

        self.securities = pd.read_csv(f, index_col="ConId").sort_values(by="Symbol")

    def _write_bars(self, daily_bar_writer, minute_bar_writer, calendar):
        raise NotImplementedError()

    def _write_assets(self, asset_db_writer):
        """
        Queries the master service and prepares the securities for the asset
        writer.
        """

        self.min_dates.name = "start_date"
        self.max_dates.name = "end_date"
        # Join min and max dates, using inner join so as not to load any
        # assets with no price history
        self.securities = self.securities.join(self.min_dates, how="inner").join(self.max_dates, how="inner")
        self.securities["first_traded"] = self.securities["start_date"]

        self.securities[["Symbol", "LocalSymbol"]] = self.securities[["Symbol", "LocalSymbol"]].astype(str)

        exchanges = pd.DataFrame(
            self.securities, columns=["PrimaryExchange","Timezone"]).drop_duplicates()
        exchanges = exchanges.rename(columns={
            "PrimaryExchange": "exchange",
            "Timezone": "timezone"
            })

        equities = self.securities[self.securities.SecType == "STK"].copy()
        if equities.empty:
            equities = None
        else:
            equities = pd.DataFrame(equities, columns=["PrimaryExchange", "Symbol", "LongName", "start_date", "end_date", "first_traded"])
            equities = equities.rename(columns={
                "PrimaryExchange": "exchange",
                "Symbol": "symbol",
                "LongName": "asset_name"
            })
            # The auto_close date is the day after the last trade.
            equities["auto_close_date"] = equities.end_date + pd.Timedelta(days=1)

        futures = self.securities[self.securities.SecType == "FUT"].copy()
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

class DailyHistoryIngester(_BaseHistoryIngester):

    def _write_bars(self, daily_bar_writer, minute_bar_writer, calendar):
        """
        Queries history and passes it to daily bar writer.
        """
        f = io.StringIO()
        download_history_file(
            self.code, f,
            start_date=self.start_date,
            end_date=self.end_date,
            universes=self.universes,
            conids=self.conids,
            exclude_universes=self.exclude_universes,
            exclude_conids=self.exclude_conids,
            fields=["Open","Close","High","Low","Volume"])
        prices = pd.read_csv(f, index_col=["Date","ConId"], parse_dates=["Date"])
        del f

        # store max and min dates for asset writer
        grouped_by_conid = prices.reset_index().groupby("ConId")
        self.max_dates = grouped_by_conid.Date.max()
        self.min_dates = grouped_by_conid.Date.min()
        del grouped_by_conid

        prices = prices.to_panel().swapaxes("items","minor").rename(minor={
            "Volume": "volume",
            "Open": "open",
            "Close": "close",
            "High": "high",
            "Low": "low"
        })

        prices = self._reindex_panel_for_mismatched_sessions(prices, daily_bar_writer)
        daily_bar_writer.write(prices.iteritems(), assets=set(prices.items), show_progress=True)

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
                   daily_bar_writer._calendar.name, self.code)

        msg = "; ".join([msg_part for msg_part in (base_msg, missing_dates_msg, extra_dates_msg) if msg_part])
        print(msg)

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

class MinutelyHistoryIngester(_BaseHistoryIngester):

    def __init__(self, *args, **kwargs):
        super(MinutelyHistoryIngester, self).__init__(*args, **kwargs)
        # Create a one-item queue for Zipline's minute_bar_writer to consume
        # items from
        self.ingestion_queue = queue.Queue(maxsize=1)
        self.ingestion_worker = None
        self.conids_with_errors = set()

    def _write_bars(self, daily_bar_writer, minute_bar_writer, calendar):
        """
        Queries history database one conid at a time and passes it to minute
        bar writer.
        """
        self.min_dates = {}
        self.max_dates = {}

        # Create a thread that will run consume securities from the queue and
        # pass to the minute_bar_writer
        self.ingestion_worker = threading.Thread(
            target=self._consume_prices,
            name="zipline_ingester",
            args=(minute_bar_writer, daily_bar_writer, calendar)
        )

        self.ingestion_worker.start()

        # Begin querying prices conid by conid
        self._enqueue_prices()

        # Place termination signal on queue
        self.ingestion_queue.put(None)

        self.ingestion_worker.join()

        if self.conids_with_errors:
            logger.error("skipped {0} securities with errors".format(len(self.conids_with_errors)))

        if not self.max_dates:
            raise NoData("No data found in {0} matching the ingestion parameters".format(
                self.code))

        # Convert min and max dates from dicts to Series for asset writer
        self.max_dates = pd.Series(self.max_dates)
        self.min_dates = pd.Series(self.min_dates)

    def _enqueue_prices(self):
        """
        Queries history one conid at a time and places the price history on
        the ingestion queue.
        """
        for conid, security in self.securities.iterrows():

            f = io.StringIO()
            try:
                download_history_file(
                    self.code, f,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    conids=[conid],
                    fields=["Open","Close","High","Low","Volume"])
            except requests.HTTPError as e:
                if "no history matches the query parameters" in repr(e):
                    print("No history to ingest for {0} {1} (conid {2})".format(
                        security.Symbol, security.SecType, conid))
                    continue
                else:
                    raise

            prices = pd.read_csv(f, index_col=["Date"], parse_dates=["Date"]).drop("ConId", axis=1)
            del f

            # Shift datetimes forward one minute. Why: In IB data, timestamps
            # refer to the start of the bar, but in Zipline they refer to the
            # end of the bar. For example, the trading activity between
            # 15:59:00 - 16:00:00 is represented in the 15:59:00 bar in IB
            # but the 16:00:00 bar in Zipline.
            prices.index = prices.index + pd.Timedelta(minutes=1)

            # store max and min dates for asset writer
            self.min_dates[conid] = prices.index[0]
            self.max_dates[conid] = prices.index[-1]

            prices = prices.rename(columns={
                "Volume": "volume",
                "Open": "open",
                "Close": "close",
                "High": "high",
                "Low": "low"
            })

            # Due to the queue size of 1, this will block if anything is
            # already on the queue. This prevents loading too much data into
            # memory.
            while True:
                try:
                    self.ingestion_queue.put((conid, security, prices), timeout=5)
                except queue.Full:
                    if self.worker_exception:
                        print("exiting main thread after exception in ingestion thread")
                        raise self.worker_exception
                else:
                    break

    def _consume_prices(self, minute_bar_writer, daily_bar_writer, calendar):
        """
        Pulls (conid, prices) from the queue and hands to Zipline for
        ingestion.
        """

        # Consume tasks from the queue
        while True:

            security = self.ingestion_queue.get()

            # None indicates to terminate the worker
            if security is None:
                break

            conid, security, prices = security

            print("Ingesting {0} bars for {1} {2} (conid {3})".format(
                len(prices.index), security.Symbol, security.SecType, conid))

            # Drop any minutes that are outside of the trading session (IB
            # data often includes bars from outside regular trading hours
            # even when regular trading hours are requested)
            prices = prices.tz_localize("UTC")
            idx = prices.index.intersection(calendar.all_minutes)
            prices = prices.reindex(index=idx)

            try:
                # Ingest minute bars
                minute_bar_writer.write_sid(conid, prices)
                # roll up minute to daily and ingest daily
                daily_prices = minute_frame_to_session_frame(prices, calendar)
                daily_prices = self._reindex_and_fillna_missing_sessions(daily_prices, calendar)
                daily_bar_writer.write([(conid, daily_prices)])
            except Exception as e:
                import traceback
                tb = traceback.format_exc()
                msg = "error ingesting {0} {1} (conid {2})".format(
                    security.Symbol, security.SecType, conid)
                print(msg)
                print(tb)
                logger.error("{0}, see detailed logs for traceback, continuing with next security".format(msg))

                self.conids_with_errors.add(conid)

    def _reindex_and_fillna_missing_sessions(self, daily_prices, calendar):
        """
        Reindexes the rolled-up daily bars to align with the trading
        calendar, and fills missing values. See docstrings in
        DailyHistoryIngester._reindex_panel_for_mismatched_sessions and
        DailyHistoryIngester.fillna_panel
        """
        required_idx = calendar.sessions_in_range(
            daily_prices.index.min(), daily_prices.index.max())

        daily_prices = daily_prices.reindex(index=required_idx)

        daily_prices.volume.fillna(0, inplace=True)
        daily_prices.close.fillna(method="ffill", inplace=True)
        daily_prices.loc[:, "open"] = daily_prices.open.fillna(daily_prices.close.shift())
        daily_prices.loc[:, "high"] = daily_prices.high.fillna(daily_prices.close.shift())
        daily_prices.loc[:, "low"] = daily_prices.low.fillna(daily_prices.close.shift())

        return daily_prices

def make_ingest_func(
    code,
    start_date=None,
    end_date=None,
    universes=None,
    conids=None,
    exclude_universes=None,
    exclude_conids=None):
    """
    Returns a bundle ingestion function.
    """

    db_config = get_db_config(code)
    bar_size = db_config.get("bar_size", None)

    if bar_size not in ("1 min", "1 day"):
        raise BadIngestionArgument(
            "Zipline requires 1 minute or 1 day bars, but {0} has {1} bars".format(
            code, bar_size)
        )

    if not universes and not conids:
        universes = db_config.get("universes", None)
        if not universes:
            raise BadIngestionArgument(
            "1 or more universes is required but {0} defines none".format(code))

    if bar_size == "1 day":
        ingester_cls = DailyHistoryIngester
    else:
        ingester_cls = MinutelyHistoryIngester

    ingester = ingester_cls(
        code,
        start_date=start_date,
        end_date=end_date,
        universes=universes,
        conids=conids,
        exclude_universes=exclude_universes,
        exclude_conids=exclude_conids
    )

    return ingester.ingest
