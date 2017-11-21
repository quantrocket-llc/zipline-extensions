# Copyright 2017 QuantRocket LLC - All Rights Reserved
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

from zipline.utils.numpy_utils import float64_dtype
from zipline.pipeline.data import Column, DataSet

class ReutersFinancials(DataSet):
    """
    Dataset representing all available Reuters financials Chart of Account
    (COA) codes. Utilizes annual fiscal periods.

    Available financials:

    Accounts Payable: LAPB
    Accounts Receivable - Trade, Net: AACR
    Accrued Expenses: LAEX
    Accumulated Depreciation, Total: ADEP
    Additional Paid-In Capital: QPIC
    Allowance for Funds Used During Const.: NAFC
    Amortization: SAMT
    Amortization of Policy Acquisition Costs: EPAC
    Capital Expenditures: SCEX
    Capital Lease Obligations: LCLO
    Cash: ACSH
    Cash & Due from Banks: ACDB
    Cash & Equivalents: ACAE
    Cash Interest Paid: SCIP
    Cash Payments: OCPD
    Cash Receipts: OCRC
    Cash Taxes Paid: SCTP
    Cash and Short Term Investments: SCSI
    Cash from Financing Activities: FTLF
    Cash from Investing Activities: ITLI
    Cash from Operating Activities: OTLO
    Changes in Working Capital: SOCF
    Common Stock, Total: SCMS
    Cost of Revenue, Total: SCOR
    Current Port. of  LT Debt/Capital Leases: LCLD
    DPS - Common Stock Primary Issue: DDPS1
    Deferred Income Tax: SBDT
    Deferred Policy Acquisition Costs: ADPA
    Deferred Taxes: OBDT
    Depreciation/Amortization: SDPR
    Depreciation/Depletion: SDED
    Diluted EPS Excluding ExtraOrd Items: SDBF
    Diluted Net Income: SDNI
    Diluted Normalized EPS: VDES
    Diluted Weighted Average Shares: SDWS
    Dilution Adjustment: SDAJ
    ESOP Debt Guarantee: QEDG
    Equity In Affiliates: CEIA
    Financing Cash Flow Items: SFCF
    Foreign Exchange Effects: SFEE
    Fuel Expense: EFEX
    Gain (Loss) on Sale of Assets: NGLA
    Goodwill, Net: AGWI
    Gross Profit: SGRP
    Income Available to Com Excl ExtraOrd: CIAC
    Income Available to Com Incl ExtraOrd: XNIC
    Insurance Receivables: APRE
    Intangibles, Net: AINT
    Interest Exp.(Inc.),Net-Operating, Total: SINN
    Interest Inc.(Exp.),Net-Non-Op., Total: SNIN
    Interest Income, Bank: SIIB
    Issuance (Retirement) of Debt, Net: FPRD
    Issuance (Retirement) of Stock, Net: FPSS
    Loan Loss Provision: ELLP
    Long Term Debt: LLTD
    Long Term Investments: SINV
    Losses, Benefits, and Adjustments, Total: SLBA
    Minority Interest: LMIN
    Minority Interest: CMIN
    Net Change in Cash: SNCC
    Net Income: NINC
    Net Income After Taxes: TIAT
    Net Income Before Extra. Items: NIBX
    Net Income Before Taxes: EIBT
    Net Income/Starting Line: ONET
    Net Interest Inc. After Loan Loss Prov.: SIAP
    Net Interest Income: ENII
    Net Investment Income: RNII
    Net Loans: ANTL
    Non-Cash Items: SNCI
    Non-Interest Expense, Bank: SNIE
    Non-Interest Income, Bank: SNII
    Note Receivable - Long Term: ALTR
    Notes Payable/Short Term Debt: LSTD
    Operating Income: SOPI
    Operations & Maintenance: EDOE
    Other Assets, Total: SOAT
    Other Bearing Liabilities, Total: SOBL
    Other Current Assets, Total: SOCA
    Other Current liabilities, Total: SOCL
    Other Earning Assets, Total: SOEA
    Other Equity, Total: SOTE
    Other Investing Cash Flow Items, Total: SICF
    Other Liabilities, Total: SLTL
    Other Long Term Assets, Total: SOLA
    Other Operating Expenses, Total: SOOE
    Other Revenue, Total: SORE
    Other, Net: SONT
    Payable/Accrued: LPBA
    Policy Liabilities: SPOL
    Preferred Stock - Non Redeemable, Net: SPRS
    Prepaid Expenses: APPY
    Property/Plant/Equipment, Total - Gross: APTC
    Property/Plant/Equipment, Total - Net: APPN
    Provision for Income Taxes: TTAX
    Realized & Unrealized Gains (Losses): RRGL
    Redeemable Preferred Stock, Total: SRPR
    Research & Development: ERAD
    Retained Earnings (Accumulated Deficit): QRED
    Revenue: SREV
    Selling/General/Admin. Expenses, Total: SSGA
    Short Term Investments: ASTI
    Tangible Book Value per Share, Common Eq: STBP
    Total Adjustments to Net Income: SANI
    Total Assets: ATOT
    Total Cash Dividends Paid: FCDP
    Total Common Shares Outstanding: QTCO
    Total Current Assets: ATCA
    Total Current Liabilities: LTCL
    Total Debt: STLD
    Total Deposits: LDBT
    Total Equity: QTLE
    Total Extraordinary Items: STXI
    Total Interest Expense: STIE
    Total Inventory: AITL
    Total Liabilities: LTLL
    Total Liabilities & Shareholders' Equity: QTEL
    Total Long Term Debt: LTTD
    Total Operating Expense: ETOE
    Total Preferred Shares Outstanding: QTPO
    Total Premiums Earned: SPRE
    Total Receivables, Net: ATRC
    Total Revenue: RTLR
    Total Short Term Borrowings: LSTB
    Total Utility Plant, Net: SUPN
    Treasury Stock - Common: QTSC
    U.S. GAAP Adjustment: CGAP
    Unrealized Gain (Loss): QUGL
    Unusual Expense (Income): SUIE

    To regenerate the column list and docstring:

    >>> from quantrocket.fundamental import list_reuters_codes
    >>> codes = list_reuters_codes(report_types=["financials"])
    >>> attrs= "\n".join(["{0} = Column(float64_dtype) # {1}".format(k,v) for k,v in codes["financials"].items()])
    >>> print(attrs)
    >>> docstring = "\n".join(["{0}: {1}".format(v,k) for k,v in sorted(codes["financials"].items(), key=lambda x: x[1])])
    >>> print(docstring)
    """

    SCMS = Column(float64_dtype) # Common Stock, Total
    VDES = Column(float64_dtype) # Diluted Normalized EPS
    SDNI = Column(float64_dtype) # Diluted Net Income
    SPRS = Column(float64_dtype) # Preferred Stock - Non Redeemable, Net
    SOPI = Column(float64_dtype) # Operating Income
    LAPB = Column(float64_dtype) # Accounts Payable
    NINC = Column(float64_dtype) # Net Income
    SOCL = Column(float64_dtype) # Other Current liabilities, Total
    ETOE = Column(float64_dtype) # Total Operating Expense
    SOLA = Column(float64_dtype) # Other Long Term Assets, Total
    SREV = Column(float64_dtype) # Revenue
    LAEX = Column(float64_dtype) # Accrued Expenses
    XNIC = Column(float64_dtype) # Income Available to Com Incl ExtraOrd
    SUIE = Column(float64_dtype) # Unusual Expense (Income)
    APTC = Column(float64_dtype) # Property/Plant/Equipment, Total - Gross
    SOBL = Column(float64_dtype) # Other Bearing Liabilities, Total
    SNII = Column(float64_dtype) # Non-Interest Income, Bank
    CEIA = Column(float64_dtype) # Equity In Affiliates
    ERAD = Column(float64_dtype) # Research & Development
    SDBF = Column(float64_dtype) # Diluted EPS Excluding ExtraOrd Items
    SDWS = Column(float64_dtype) # Diluted Weighted Average Shares
    SORE = Column(float64_dtype) # Other Revenue, Total
    SCEX = Column(float64_dtype) # Capital Expenditures
    ELLP = Column(float64_dtype) # Loan Loss Provision
    ACSH = Column(float64_dtype) # Cash
    AACR = Column(float64_dtype) # Accounts Receivable - Trade, Net
    SCOR = Column(float64_dtype) # Cost of Revenue, Total
    SUPN = Column(float64_dtype) # Total Utility Plant, Net
    EIBT = Column(float64_dtype) # Net Income Before Taxes
    AGWI = Column(float64_dtype) # Goodwill, Net
    SCIP = Column(float64_dtype) # Cash Interest Paid
    SDED = Column(float64_dtype) # Depreciation/Depletion
    RNII = Column(float64_dtype) # Net Investment Income
    ADPA = Column(float64_dtype) # Deferred Policy Acquisition Costs
    SONT = Column(float64_dtype) # Other, Net
    CGAP = Column(float64_dtype) # U.S. GAAP Adjustment
    AINT = Column(float64_dtype) # Intangibles, Net
    SGRP = Column(float64_dtype) # Gross Profit
    SNIE = Column(float64_dtype) # Non-Interest Expense, Bank
    EDOE = Column(float64_dtype) # Operations & Maintenance
    SSGA = Column(float64_dtype) # Selling/General/Admin. Expenses, Total
    SNIN = Column(float64_dtype) # Interest Inc.(Exp.),Net-Non-Op., Total
    QTSC = Column(float64_dtype) # Treasury Stock - Common
    OCPD = Column(float64_dtype) # Cash Payments
    OBDT = Column(float64_dtype) # Deferred Taxes
    TTAX = Column(float64_dtype) # Provision for Income Taxes
    LPBA = Column(float64_dtype) # Payable/Accrued
    QRED = Column(float64_dtype) # Retained Earnings (Accumulated Deficit)
    SCSI = Column(float64_dtype) # Cash and Short Term Investments
    SIAP = Column(float64_dtype) # Net Interest Inc. After Loan Loss Prov.
    ANTL = Column(float64_dtype) # Net Loans
    QTCO = Column(float64_dtype) # Total Common Shares Outstanding
    LDBT = Column(float64_dtype) # Total Deposits
    SANI = Column(float64_dtype) # Total Adjustments to Net Income
    AITL = Column(float64_dtype) # Total Inventory
    ATRC = Column(float64_dtype) # Total Receivables, Net
    SBDT = Column(float64_dtype) # Deferred Income Tax
    ASTI = Column(float64_dtype) # Short Term Investments
    OTLO = Column(float64_dtype) # Cash from Operating Activities
    OCRC = Column(float64_dtype) # Cash Receipts
    RRGL = Column(float64_dtype) # Realized & Unrealized Gains (Losses)
    STLD = Column(float64_dtype) # Total Debt
    LTTD = Column(float64_dtype) # Total Long Term Debt
    LTLL = Column(float64_dtype) # Total Liabilities
    APPN = Column(float64_dtype) # Property/Plant/Equipment, Total - Net
    SCTP = Column(float64_dtype) # Cash Taxes Paid
    SLTL = Column(float64_dtype) # Other Liabilities, Total
    DDPS1 = Column(float64_dtype) # DPS - Common Stock Primary Issue
    SRPR = Column(float64_dtype) # Redeemable Preferred Stock, Total
    ITLI = Column(float64_dtype) # Cash from Investing Activities
    ONET = Column(float64_dtype) # Net Income/Starting Line
    SDPR = Column(float64_dtype) # Depreciation/Amortization
    STIE = Column(float64_dtype) # Total Interest Expense
    APRE = Column(float64_dtype) # Insurance Receivables
    SNCC = Column(float64_dtype) # Net Change in Cash
    SFCF = Column(float64_dtype) # Financing Cash Flow Items
    SINN = Column(float64_dtype) # Interest Exp.(Inc.),Net-Operating, Total
    CMIN = Column(float64_dtype) # Minority Interest
    SOAT = Column(float64_dtype) # Other Assets, Total
    SNCI = Column(float64_dtype) # Non-Cash Items
    LCLD = Column(float64_dtype) # Current Port. of  LT Debt/Capital Leases
    SDAJ = Column(float64_dtype) # Dilution Adjustment
    SIIB = Column(float64_dtype) # Interest Income, Bank
    QUGL = Column(float64_dtype) # Unrealized Gain (Loss)
    NIBX = Column(float64_dtype) # Net Income Before Extra. Items
    SOOE = Column(float64_dtype) # Other Operating Expenses, Total
    SAMT = Column(float64_dtype) # Amortization
    SFEE = Column(float64_dtype) # Foreign Exchange Effects
    STXI = Column(float64_dtype) # Total Extraordinary Items
    APPY = Column(float64_dtype) # Prepaid Expenses
    EFEX = Column(float64_dtype) # Fuel Expense
    QTPO = Column(float64_dtype) # Total Preferred Shares Outstanding
    NGLA = Column(float64_dtype) # Gain (Loss) on Sale of Assets
    SINV = Column(float64_dtype) # Long Term Investments
    SOCA = Column(float64_dtype) # Other Current Assets, Total
    FCDP = Column(float64_dtype) # Total Cash Dividends Paid
    FPSS = Column(float64_dtype) # Issuance (Retirement) of Stock, Net
    RTLR = Column(float64_dtype) # Total Revenue
    ACDB = Column(float64_dtype) # Cash & Due from Banks
    TIAT = Column(float64_dtype) # Net Income After Taxes
    SOEA = Column(float64_dtype) # Other Earning Assets, Total
    SOTE = Column(float64_dtype) # Other Equity, Total
    SPOL = Column(float64_dtype) # Policy Liabilities
    NAFC = Column(float64_dtype) # Allowance for Funds Used During Const.
    QPIC = Column(float64_dtype) # Additional Paid-In Capital
    QTLE = Column(float64_dtype) # Total Equity
    ACAE = Column(float64_dtype) # Cash & Equivalents
    FPRD = Column(float64_dtype) # Issuance (Retirement) of Debt, Net
    ALTR = Column(float64_dtype) # Note Receivable - Long Term
    SLBA = Column(float64_dtype) # Losses, Benefits, and Adjustments, Total
    ATCA = Column(float64_dtype) # Total Current Assets
    SOCF = Column(float64_dtype) # Changes in Working Capital
    LCLO = Column(float64_dtype) # Capital Lease Obligations
    LSTD = Column(float64_dtype) # Notes Payable/Short Term Debt
    STBP = Column(float64_dtype) # Tangible Book Value per Share, Common Eq
    SICF = Column(float64_dtype) # Other Investing Cash Flow Items, Total
    ENII = Column(float64_dtype) # Net Interest Income
    QTEL = Column(float64_dtype) # Total Liabilities & Shareholders' Equity
    FTLF = Column(float64_dtype) # Cash from Financing Activities
    LTCL = Column(float64_dtype) # Total Current Liabilities
    SPRE = Column(float64_dtype) # Total Premiums Earned
    LSTB = Column(float64_dtype) # Total Short Term Borrowings
    EPAC = Column(float64_dtype) # Amortization of Policy Acquisition Costs
    LLTD = Column(float64_dtype) # Long Term Debt
    ATOT = Column(float64_dtype) # Total Assets
    CIAC = Column(float64_dtype) # Income Available to Com Excl ExtraOrd
    QEDG = Column(float64_dtype) # ESOP Debt Guarantee
    LMIN = Column(float64_dtype) # Minority Interest
    ADEP = Column(float64_dtype) # Accumulated Depreciation, Total

class ReutersInterimFinancials(DataSet):
    """
    Dataset representing all available Reuters financials Chart of Account
    (COA) codes. Utilizes interim fiscal periods.

    Available financials:

    Accounts Payable: LAPB
    Accounts Receivable - Trade, Net: AACR
    Accrued Expenses: LAEX
    Accumulated Depreciation, Total: ADEP
    Additional Paid-In Capital: QPIC
    Allowance for Funds Used During Const.: NAFC
    Amortization: SAMT
    Amortization of Policy Acquisition Costs: EPAC
    Capital Expenditures: SCEX
    Capital Lease Obligations: LCLO
    Cash: ACSH
    Cash & Due from Banks: ACDB
    Cash & Equivalents: ACAE
    Cash Interest Paid: SCIP
    Cash Payments: OCPD
    Cash Receipts: OCRC
    Cash Taxes Paid: SCTP
    Cash and Short Term Investments: SCSI
    Cash from Financing Activities: FTLF
    Cash from Investing Activities: ITLI
    Cash from Operating Activities: OTLO
    Changes in Working Capital: SOCF
    Common Stock, Total: SCMS
    Cost of Revenue, Total: SCOR
    Current Port. of  LT Debt/Capital Leases: LCLD
    DPS - Common Stock Primary Issue: DDPS1
    Deferred Income Tax: SBDT
    Deferred Policy Acquisition Costs: ADPA
    Deferred Taxes: OBDT
    Depreciation/Amortization: SDPR
    Depreciation/Depletion: SDED
    Diluted EPS Excluding ExtraOrd Items: SDBF
    Diluted Net Income: SDNI
    Diluted Normalized EPS: VDES
    Diluted Weighted Average Shares: SDWS
    Dilution Adjustment: SDAJ
    ESOP Debt Guarantee: QEDG
    Equity In Affiliates: CEIA
    Financing Cash Flow Items: SFCF
    Foreign Exchange Effects: SFEE
    Fuel Expense: EFEX
    Gain (Loss) on Sale of Assets: NGLA
    Goodwill, Net: AGWI
    Gross Profit: SGRP
    Income Available to Com Excl ExtraOrd: CIAC
    Income Available to Com Incl ExtraOrd: XNIC
    Insurance Receivables: APRE
    Intangibles, Net: AINT
    Interest Exp.(Inc.),Net-Operating, Total: SINN
    Interest Inc.(Exp.),Net-Non-Op., Total: SNIN
    Interest Income, Bank: SIIB
    Issuance (Retirement) of Debt, Net: FPRD
    Issuance (Retirement) of Stock, Net: FPSS
    Loan Loss Provision: ELLP
    Long Term Debt: LLTD
    Long Term Investments: SINV
    Losses, Benefits, and Adjustments, Total: SLBA
    Minority Interest: LMIN
    Minority Interest: CMIN
    Net Change in Cash: SNCC
    Net Income: NINC
    Net Income After Taxes: TIAT
    Net Income Before Extra. Items: NIBX
    Net Income Before Taxes: EIBT
    Net Income/Starting Line: ONET
    Net Interest Inc. After Loan Loss Prov.: SIAP
    Net Interest Income: ENII
    Net Investment Income: RNII
    Net Loans: ANTL
    Non-Cash Items: SNCI
    Non-Interest Expense, Bank: SNIE
    Non-Interest Income, Bank: SNII
    Note Receivable - Long Term: ALTR
    Notes Payable/Short Term Debt: LSTD
    Operating Income: SOPI
    Operations & Maintenance: EDOE
    Other Assets, Total: SOAT
    Other Bearing Liabilities, Total: SOBL
    Other Current Assets, Total: SOCA
    Other Current liabilities, Total: SOCL
    Other Earning Assets, Total: SOEA
    Other Equity, Total: SOTE
    Other Investing Cash Flow Items, Total: SICF
    Other Liabilities, Total: SLTL
    Other Long Term Assets, Total: SOLA
    Other Operating Expenses, Total: SOOE
    Other Revenue, Total: SORE
    Other, Net: SONT
    Payable/Accrued: LPBA
    Policy Liabilities: SPOL
    Preferred Stock - Non Redeemable, Net: SPRS
    Prepaid Expenses: APPY
    Property/Plant/Equipment, Total - Gross: APTC
    Property/Plant/Equipment, Total - Net: APPN
    Provision for Income Taxes: TTAX
    Realized & Unrealized Gains (Losses): RRGL
    Redeemable Preferred Stock, Total: SRPR
    Research & Development: ERAD
    Retained Earnings (Accumulated Deficit): QRED
    Revenue: SREV
    Selling/General/Admin. Expenses, Total: SSGA
    Short Term Investments: ASTI
    Tangible Book Value per Share, Common Eq: STBP
    Total Adjustments to Net Income: SANI
    Total Assets: ATOT
    Total Cash Dividends Paid: FCDP
    Total Common Shares Outstanding: QTCO
    Total Current Assets: ATCA
    Total Current Liabilities: LTCL
    Total Debt: STLD
    Total Deposits: LDBT
    Total Equity: QTLE
    Total Extraordinary Items: STXI
    Total Interest Expense: STIE
    Total Inventory: AITL
    Total Liabilities: LTLL
    Total Liabilities & Shareholders' Equity: QTEL
    Total Long Term Debt: LTTD
    Total Operating Expense: ETOE
    Total Preferred Shares Outstanding: QTPO
    Total Premiums Earned: SPRE
    Total Receivables, Net: ATRC
    Total Revenue: RTLR
    Total Short Term Borrowings: LSTB
    Total Utility Plant, Net: SUPN
    Treasury Stock - Common: QTSC
    U.S. GAAP Adjustment: CGAP
    Unrealized Gain (Loss): QUGL
    Unusual Expense (Income): SUIE

    To regenerate the column list and docstring:

    >>> from quantrocket.fundamental import list_reuters_codes
    >>> codes = list_reuters_codes(report_types=["financials"])
    >>> attrs= "\n".join(["{0} = Column(float64_dtype) # {1}".format(k,v) for k,v in codes["financials"].items()])
    >>> print(attrs)
    >>> docstring = "\n".join(["{0}: {1}".format(v,k) for k,v in sorted(codes["financials"].items(), key=lambda x: x[1])])
    >>> print(docstring)
    """

    SCMS = Column(float64_dtype) # Common Stock, Total
    VDES = Column(float64_dtype) # Diluted Normalized EPS
    SDNI = Column(float64_dtype) # Diluted Net Income
    SPRS = Column(float64_dtype) # Preferred Stock - Non Redeemable, Net
    SOPI = Column(float64_dtype) # Operating Income
    LAPB = Column(float64_dtype) # Accounts Payable
    NINC = Column(float64_dtype) # Net Income
    SOCL = Column(float64_dtype) # Other Current liabilities, Total
    ETOE = Column(float64_dtype) # Total Operating Expense
    SOLA = Column(float64_dtype) # Other Long Term Assets, Total
    SREV = Column(float64_dtype) # Revenue
    LAEX = Column(float64_dtype) # Accrued Expenses
    XNIC = Column(float64_dtype) # Income Available to Com Incl ExtraOrd
    SUIE = Column(float64_dtype) # Unusual Expense (Income)
    APTC = Column(float64_dtype) # Property/Plant/Equipment, Total - Gross
    SOBL = Column(float64_dtype) # Other Bearing Liabilities, Total
    SNII = Column(float64_dtype) # Non-Interest Income, Bank
    CEIA = Column(float64_dtype) # Equity In Affiliates
    ERAD = Column(float64_dtype) # Research & Development
    SDBF = Column(float64_dtype) # Diluted EPS Excluding ExtraOrd Items
    SDWS = Column(float64_dtype) # Diluted Weighted Average Shares
    SORE = Column(float64_dtype) # Other Revenue, Total
    SCEX = Column(float64_dtype) # Capital Expenditures
    ELLP = Column(float64_dtype) # Loan Loss Provision
    ACSH = Column(float64_dtype) # Cash
    AACR = Column(float64_dtype) # Accounts Receivable - Trade, Net
    SCOR = Column(float64_dtype) # Cost of Revenue, Total
    SUPN = Column(float64_dtype) # Total Utility Plant, Net
    EIBT = Column(float64_dtype) # Net Income Before Taxes
    AGWI = Column(float64_dtype) # Goodwill, Net
    SCIP = Column(float64_dtype) # Cash Interest Paid
    SDED = Column(float64_dtype) # Depreciation/Depletion
    RNII = Column(float64_dtype) # Net Investment Income
    ADPA = Column(float64_dtype) # Deferred Policy Acquisition Costs
    SONT = Column(float64_dtype) # Other, Net
    CGAP = Column(float64_dtype) # U.S. GAAP Adjustment
    AINT = Column(float64_dtype) # Intangibles, Net
    SGRP = Column(float64_dtype) # Gross Profit
    SNIE = Column(float64_dtype) # Non-Interest Expense, Bank
    EDOE = Column(float64_dtype) # Operations & Maintenance
    SSGA = Column(float64_dtype) # Selling/General/Admin. Expenses, Total
    SNIN = Column(float64_dtype) # Interest Inc.(Exp.),Net-Non-Op., Total
    QTSC = Column(float64_dtype) # Treasury Stock - Common
    OCPD = Column(float64_dtype) # Cash Payments
    OBDT = Column(float64_dtype) # Deferred Taxes
    TTAX = Column(float64_dtype) # Provision for Income Taxes
    LPBA = Column(float64_dtype) # Payable/Accrued
    QRED = Column(float64_dtype) # Retained Earnings (Accumulated Deficit)
    SCSI = Column(float64_dtype) # Cash and Short Term Investments
    SIAP = Column(float64_dtype) # Net Interest Inc. After Loan Loss Prov.
    ANTL = Column(float64_dtype) # Net Loans
    QTCO = Column(float64_dtype) # Total Common Shares Outstanding
    LDBT = Column(float64_dtype) # Total Deposits
    SANI = Column(float64_dtype) # Total Adjustments to Net Income
    AITL = Column(float64_dtype) # Total Inventory
    ATRC = Column(float64_dtype) # Total Receivables, Net
    SBDT = Column(float64_dtype) # Deferred Income Tax
    ASTI = Column(float64_dtype) # Short Term Investments
    OTLO = Column(float64_dtype) # Cash from Operating Activities
    OCRC = Column(float64_dtype) # Cash Receipts
    RRGL = Column(float64_dtype) # Realized & Unrealized Gains (Losses)
    STLD = Column(float64_dtype) # Total Debt
    LTTD = Column(float64_dtype) # Total Long Term Debt
    LTLL = Column(float64_dtype) # Total Liabilities
    APPN = Column(float64_dtype) # Property/Plant/Equipment, Total - Net
    SCTP = Column(float64_dtype) # Cash Taxes Paid
    SLTL = Column(float64_dtype) # Other Liabilities, Total
    DDPS1 = Column(float64_dtype) # DPS - Common Stock Primary Issue
    SRPR = Column(float64_dtype) # Redeemable Preferred Stock, Total
    ITLI = Column(float64_dtype) # Cash from Investing Activities
    ONET = Column(float64_dtype) # Net Income/Starting Line
    SDPR = Column(float64_dtype) # Depreciation/Amortization
    STIE = Column(float64_dtype) # Total Interest Expense
    APRE = Column(float64_dtype) # Insurance Receivables
    SNCC = Column(float64_dtype) # Net Change in Cash
    SFCF = Column(float64_dtype) # Financing Cash Flow Items
    SINN = Column(float64_dtype) # Interest Exp.(Inc.),Net-Operating, Total
    CMIN = Column(float64_dtype) # Minority Interest
    SOAT = Column(float64_dtype) # Other Assets, Total
    SNCI = Column(float64_dtype) # Non-Cash Items
    LCLD = Column(float64_dtype) # Current Port. of  LT Debt/Capital Leases
    SDAJ = Column(float64_dtype) # Dilution Adjustment
    SIIB = Column(float64_dtype) # Interest Income, Bank
    QUGL = Column(float64_dtype) # Unrealized Gain (Loss)
    NIBX = Column(float64_dtype) # Net Income Before Extra. Items
    SOOE = Column(float64_dtype) # Other Operating Expenses, Total
    SAMT = Column(float64_dtype) # Amortization
    SFEE = Column(float64_dtype) # Foreign Exchange Effects
    STXI = Column(float64_dtype) # Total Extraordinary Items
    APPY = Column(float64_dtype) # Prepaid Expenses
    EFEX = Column(float64_dtype) # Fuel Expense
    QTPO = Column(float64_dtype) # Total Preferred Shares Outstanding
    NGLA = Column(float64_dtype) # Gain (Loss) on Sale of Assets
    SINV = Column(float64_dtype) # Long Term Investments
    SOCA = Column(float64_dtype) # Other Current Assets, Total
    FCDP = Column(float64_dtype) # Total Cash Dividends Paid
    FPSS = Column(float64_dtype) # Issuance (Retirement) of Stock, Net
    RTLR = Column(float64_dtype) # Total Revenue
    ACDB = Column(float64_dtype) # Cash & Due from Banks
    TIAT = Column(float64_dtype) # Net Income After Taxes
    SOEA = Column(float64_dtype) # Other Earning Assets, Total
    SOTE = Column(float64_dtype) # Other Equity, Total
    SPOL = Column(float64_dtype) # Policy Liabilities
    NAFC = Column(float64_dtype) # Allowance for Funds Used During Const.
    QPIC = Column(float64_dtype) # Additional Paid-In Capital
    QTLE = Column(float64_dtype) # Total Equity
    ACAE = Column(float64_dtype) # Cash & Equivalents
    FPRD = Column(float64_dtype) # Issuance (Retirement) of Debt, Net
    ALTR = Column(float64_dtype) # Note Receivable - Long Term
    SLBA = Column(float64_dtype) # Losses, Benefits, and Adjustments, Total
    ATCA = Column(float64_dtype) # Total Current Assets
    SOCF = Column(float64_dtype) # Changes in Working Capital
    LCLO = Column(float64_dtype) # Capital Lease Obligations
    LSTD = Column(float64_dtype) # Notes Payable/Short Term Debt
    STBP = Column(float64_dtype) # Tangible Book Value per Share, Common Eq
    SICF = Column(float64_dtype) # Other Investing Cash Flow Items, Total
    ENII = Column(float64_dtype) # Net Interest Income
    QTEL = Column(float64_dtype) # Total Liabilities & Shareholders' Equity
    FTLF = Column(float64_dtype) # Cash from Financing Activities
    LTCL = Column(float64_dtype) # Total Current Liabilities
    SPRE = Column(float64_dtype) # Total Premiums Earned
    LSTB = Column(float64_dtype) # Total Short Term Borrowings
    EPAC = Column(float64_dtype) # Amortization of Policy Acquisition Costs
    LLTD = Column(float64_dtype) # Long Term Debt
    ATOT = Column(float64_dtype) # Total Assets
    CIAC = Column(float64_dtype) # Income Available to Com Excl ExtraOrd
    QEDG = Column(float64_dtype) # ESOP Debt Guarantee
    LMIN = Column(float64_dtype) # Minority Interest
    ADEP = Column(float64_dtype) # Accumulated Depreciation, Total
