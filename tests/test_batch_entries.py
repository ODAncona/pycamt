"""Tests focused on the `Ntry -> NtryDtls -> Btch/TxDtls` relationship.

This module specifically targets the scenario described by the user: large
CRDT entries (e.g. salary batches, grouped standing orders) encoded by Swiss
banks using a `<Btch>` (batch summary) element instead of, or in addition to,
individual `<TxDtls>` elements. If the parser silently drops or miscounts
these entries, the running balance computed from `(CRDT - DBIT).cumsum()`
will drift away from the real account balance -- which is exactly the
"trou de 84'000 balles" symptom reported by the user.
"""

from pycamt.parser import Camt053Parser


def _wrap(entries_xml: str) -> str:
    return f"""
    <Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.04">
        <BkToCstmrStmt>
            <GrpHdr>
                <MsgId>MSG001</MsgId>
                <CreDtTm>2021-05-01T00:00:00</CreDtTm>
            </GrpHdr>
            <Stmt>
                <Acct>
                    <Id>
                        <IBAN>CH9300762011623852957</IBAN>
                    </Id>
                    <Ccy>CHF</Ccy>
                </Acct>
                <Bal>
                    <Tp><CdOrPrtry><Cd>OPBD</Cd></CdOrPrtry></Tp>
                    <Dt><Dt>2021-04-30</Dt></Dt>
                    <Amt Ccy="CHF">0.00</Amt>
                    <CdtDbtInd>CRDT</CdtDbtInd>
                </Bal>
                <Bal>
                    <Tp><CdOrPrtry><Cd>CLBD</Cd></CdOrPrtry></Tp>
                    <Dt><Dt>2021-05-31</Dt></Dt>
                    <Amt Ccy="CHF">4000.00</Amt>
                    <CdtDbtInd>CRDT</CdtDbtInd>
                </Bal>
                {entries_xml}
            </Stmt>
        </BkToCstmrStmt>
    </Document>
    """


class TestBatchOnlyEntry:
    """Entry whose NtryDtls only contains a <Btch> summary, no <TxDtls>.

    This is the typical encoding for a salary payment lot: the bank reports
    the aggregated amount only, without breaking it down transaction by
    transaction. If the parser expects a <TxDtls> to be always present, this
    entry (and its whole amount) would be silently lost.
    """

    def _entry_xml(self, amount="88000.00", indicator="CRDT"):
        return f"""
        <Ntry>
            <Amt Ccy="CHF">{amount}</Amt>
            <CdtDbtInd>{indicator}</CdtDbtInd>
            <Sts>BOOK</Sts>
            <BookgDt><Dt>2021-05-01</Dt></BookgDt>
            <ValDt><Dt>2021-05-01</Dt></ValDt>
            <AcctSvcrRef>BATCH001</AcctSvcrRef>
            <BkTxCd>
                <Domn>
                    <Cd>PMNT</Cd>
                    <Fmly>
                        <Cd>RCDT</Cd>
                        <SubFmlyCd>SALA</SubFmlyCd>
                    </Fmly>
                </Domn>
            </BkTxCd>
            <NtryDtls>
                <Btch>
                    <NbOfTxs>42</NbOfTxs>
                    <TtlAmt Ccy="CHF">{amount}</TtlAmt>
                    <CdtDbtInd>{indicator}</CdtDbtInd>
                </Btch>
            </NtryDtls>
            <AddtlNtryInf>Salaires lot mai 2021</AddtlNtryInf>
        </Ntry>
        """

    def test_batch_only_credit_entry_is_captured(self):
        """The 88'000 CHF batch credit must appear exactly once, with the
        full amount and the correct CRDT indicator."""
        xml_data = _wrap(self._entry_xml(amount="88000.00", indicator="CRDT"))
        parser = Camt053Parser(xml_data)
        transactions = parser.get_transactions()

        assert len(transactions) == 1
        tx = transactions[0]
        assert tx["Amount"] == "88000.00"
        assert tx["CreditDebitIndicator"] == "CRDT"
        assert tx["TransactionID"] == "BATCH001"

    def test_batch_only_debit_entry_is_captured(self):
        xml_data = _wrap(self._entry_xml(amount="123.20", indicator="DBIT"))
        parser = Camt053Parser(xml_data)
        transactions = parser.get_transactions()

        assert len(transactions) == 1
        assert transactions[0]["Amount"] == "123.20"
        assert transactions[0]["CreditDebitIndicator"] == "DBIT"

    def test_batch_entry_not_duplicated(self):
        """Regression guard: an entry with a Btch-only NtryDtls must not be
        returned twice (once for the fallback, once for a spurious tx)."""
        xml_data = _wrap(self._entry_xml())
        parser = Camt053Parser(xml_data)
        transactions = parser.get_transactions()

        assert len(transactions) == 1


class TestNoDetailsEntry:
    """Entry with no <NtryDtls> at all (pure 1-0 relationship)."""

    def test_entry_without_ntrydtls(self):
        entry_xml = """
        <Ntry>
            <Amt Ccy="CHF">2500.00</Amt>
            <CdtDbtInd>CRDT</CdtDbtInd>
            <BookgDt><Dt>2021-05-01</Dt></BookgDt>
            <ValDt><Dt>2021-05-01</Dt></ValDt>
            <AcctSvcrRef>NODETAILS001</AcctSvcrRef>
        </Ntry>
        """
        xml_data = _wrap(entry_xml)
        parser = Camt053Parser(xml_data)
        transactions = parser.get_transactions()

        assert len(transactions) == 1
        assert transactions[0]["Amount"] == "2500.00"
        assert transactions[0]["CreditDebitIndicator"] == "CRDT"


class TestMixedNtryDtls:
    """An entry can contain several <NtryDtls>, some with a Btch summary
    only, others with actual <TxDtls>. All information must be preserved
    without dropping the batch-only part.
    """

    def test_batch_and_txdtls_side_by_side(self):
        entry_xml = """
        <Ntry>
            <Amt Ccy="CHF">1500.00</Amt>
            <CdtDbtInd>DBIT</CdtDbtInd>
            <BookgDt><Dt>2021-05-02</Dt></BookgDt>
            <ValDt><Dt>2021-05-02</Dt></ValDt>
            <AcctSvcrRef>MIXED001</AcctSvcrRef>
            <NtryDtls>
                <Btch>
                    <NbOfTxs>2</NbOfTxs>
                    <TtlAmt Ccy="CHF">1500.00</TtlAmt>
                    <CdtDbtInd>DBIT</CdtDbtInd>
                </Btch>
                <TxDtls>
                    <Refs>
                        <EndToEndId>E2E-001</EndToEndId>
                    </Refs>
                    <Amt Ccy="CHF">1000.00</Amt>
                    <CdtDbtInd>DBIT</CdtDbtInd>
                    <RltdPties>
                        <Cdtr><Nm>Landlord SA</Nm></Cdtr>
                    </RltdPties>
                </TxDtls>
                <TxDtls>
                    <Refs>
                        <EndToEndId>E2E-002</EndToEndId>
                    </Refs>
                    <Amt Ccy="CHF">500.00</Amt>
                    <CdtDbtInd>DBIT</CdtDbtInd>
                    <RltdPties>
                        <Cdtr><Nm>Insurance SA</Nm></Cdtr>
                    </RltdPties>
                </TxDtls>
            </NtryDtls>
        </Ntry>
        """
        xml_data = _wrap(entry_xml)
        parser = Camt053Parser(xml_data)
        transactions = parser.get_transactions()

        # The Btch-only NtryDtls contributes no TxDtls, so it must not
        # generate a spurious extra transaction: exactly the 2 TxDtls-based
        # transactions are expected.
        assert len(transactions) == 2
        amounts = sorted(float(tx["Amount"]) for tx in transactions)
        assert amounts == [500.00, 1000.00]

    def test_divergent_credit_debit_indicator_between_entry_and_detail(self):
        """Safety-net check for the '# SÉCURITÉ' logic: when a TxDtls has its
        own CdtDbtInd, it must override the entry-level indicator on the
        resulting transaction (this can happen for reversal/correction
        entries).
        """
        entry_xml = """
        <Ntry>
            <Amt Ccy="CHF">300.00</Amt>
            <CdtDbtInd>CRDT</CdtDbtInd>
            <BookgDt><Dt>2021-05-03</Dt></BookgDt>
            <ValDt><Dt>2021-05-03</Dt></ValDt>
            <AcctSvcrRef>DIVERGENT001</AcctSvcrRef>
            <NtryDtls>
                <TxDtls>
                    <Refs>
                        <EndToEndId>E2E-003</EndToEndId>
                    </Refs>
                    <Amt Ccy="CHF">300.00</Amt>
                    <CdtDbtInd>DBIT</CdtDbtInd>
                </TxDtls>
            </NtryDtls>
        </Ntry>
        """
        xml_data = _wrap(entry_xml)
        parser = Camt053Parser(xml_data)
        transactions = parser.get_transactions()

        assert len(transactions) == 1
        # The detail-level indicator wins over the entry-level one.
        assert transactions[0]["CreditDebitIndicator"] == "DBIT"


class TestMissingOptionalFields:
    """Regression tests for real-world entries observed in production bank
    exports where fields long assumed to be "always present" are actually
    absent.

    This reproduces the exact crash reported in production:

        AttributeError: 'NoneType' object has no attribute 'text'
        ... entry.find(".//AcctSvcrRef", self.namespaces).text

    A forensic audit of a real ~3000-entry CAMT.053 export found 50 entries
    (~1.6%) without <AcctSvcrRef>, mostly year-end interest postings (e.g.
    0.02 CHF credited on Dec 31st) and small internal adjustments. Per the
    ISO 20022 schema, AcctSvcrRef has cardinality 0..1 so this is legit,
    not a malformed file -- the parser must not crash on it.
    """

    def test_entry_without_acctsvcrref_does_not_crash(self):
        """Exact reproduction of the reported production crash: a CRDT
        year-end interest entry with TxDtls but no <AcctSvcrRef>."""
        entry_xml = """
        <Ntry>
            <Amt Ccy="CHF">.02</Amt>
            <CdtDbtInd>CRDT</CdtDbtInd>
            <RvslInd>false</RvslInd>
            <Sts>BOOK</Sts>
            <BookgDt><Dt>2023-12-31</Dt></BookgDt>
            <ValDt><Dt>2023-12-31</Dt></ValDt>
            <BkTxCd>
                <Domn>
                    <Cd>PMNT</Cd>
                    <Fmly>
                        <Cd>RCDT</Cd>
                        <SubFmlyCd>OTHR</SubFmlyCd>
                    </Fmly>
                </Domn>
            </BkTxCd>
            <NtryDtls>
                <TxDtls>
                    <Refs>
                        <InstrId>NOTPROVIDED</InstrId>
                        <EndToEndId>NOTPROVIDED</EndToEndId>
                    </Refs>
                    <Amt Ccy="CHF">.02</Amt>
                    <CdtDbtInd>CRDT</CdtDbtInd>
                </TxDtls>
            </NtryDtls>
        </Ntry>
        """
        xml_data = _wrap(entry_xml)
        parser = Camt053Parser(xml_data)

        # Must not raise AttributeError: 'NoneType' object has no attribute 'text'
        transactions = parser.get_transactions()

        assert len(transactions) == 1
        tx = transactions[0]
        assert tx["Amount"] == ".02"
        assert tx["CreditDebitIndicator"] == "CRDT"
        assert tx["TransactionID"] is None
        assert tx["BookingDate"] == "2023-12-31"
        assert tx["ValueDate"] == "2023-12-31"

    def test_entry_without_bookgdt_and_valdt(self):
        """BookgDt / ValDt missing entirely at the entry level."""
        entry_xml = """
        <Ntry>
            <Amt Ccy="CHF">100.00</Amt>
            <CdtDbtInd>DBIT</CdtDbtInd>
            <AcctSvcrRef>REF999</AcctSvcrRef>
        </Ntry>
        """
        xml_data = _wrap(entry_xml)
        parser = Camt053Parser(xml_data)

        transactions = parser.get_transactions()

        assert len(transactions) == 1
        tx = transactions[0]
        assert tx["Amount"] == "100.00"
        assert tx["BookingDate"] is None
        assert tx["ValueDate"] is None

    def test_entry_without_amt_or_cdtdbtind(self):
        """Even the theoretically-mandatory Amt/CdtDbtInd should degrade to
        None rather than crash -- better a partial row than a full parsing
        failure on a large real-world file."""
        entry_xml = """
        <Ntry>
            <AcctSvcrRef>REF888</AcctSvcrRef>
            <BookgDt><Dt>2024-01-01</Dt></BookgDt>
            <ValDt><Dt>2024-01-01</Dt></ValDt>
        </Ntry>
        """
        xml_data = _wrap(entry_xml)
        parser = Camt053Parser(xml_data)

        transactions = parser.get_transactions()

        assert len(transactions) == 1
        tx = transactions[0]
        assert tx["Amount"] is None
        assert tx["Currency"] is None
        assert tx["CreditDebitIndicator"] is None
        assert tx["TransactionID"] == "REF888"

    def test_multiple_fields_missing_combined(self):
        """Combination of several missing optional fields on the same
        entry, as seen in the real audited file (interest/adjustment
        entries lacking AcctSvcrRef, BkTxCd sub-fields, etc.)."""
        entry_xml = """
        <Ntry>
            <Amt Ccy="CHF">1.70</Amt>
            <CdtDbtInd>CRDT</CdtDbtInd>
            <Sts>BOOK</Sts>
            <BookgDt><Dt>2024-12-31</Dt></BookgDt>
            <ValDt><Dt>2024-12-31</Dt></ValDt>
        </Ntry>
        """
        xml_data = _wrap(entry_xml)
        parser = Camt053Parser(xml_data)

        transactions = parser.get_transactions()

        assert len(transactions) == 1
        tx = transactions[0]
        assert tx["Amount"] == "1.70"
        assert tx["TransactionID"] is None
        assert tx["BankTransactionCode"] is None
        assert tx["TransactionFamilyCode"] is None
        assert tx["TransactionSubFamilyCode"] is None

    def test_entry_without_amt_element_leaves_currency_none(self):
        """When <Amt> itself is fully absent, the Currency (derived from
        Amt's Ccy attribute) must also degrade to None instead of raising
        AttributeError on a None attrib lookup."""
        entry_xml = """
        <Ntry>
            <CdtDbtInd>CRDT</CdtDbtInd>
            <AcctSvcrRef>REF777</AcctSvcrRef>
        </Ntry>
        """
        xml_data = _wrap(entry_xml)
        parser = Camt053Parser(xml_data)

        transactions = parser.get_transactions()

        assert len(transactions) == 1
        assert transactions[0]["Amount"] is None
        assert transactions[0]["Currency"] is None

    def test_statement_without_acct_element(self):
        """AccountIBAN must degrade to None if the Stmt has no <Acct> at all
        (covers the `element is None` branch of the _find_text helper)."""
        xml_data = """
        <Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.04">
            <BkToCstmrStmt>
                <GrpHdr>
                    <MsgId>MSG002</MsgId>
                    <CreDtTm>2021-05-01T00:00:00</CreDtTm>
                </GrpHdr>
                <Stmt>
                    <Ntry>
                        <Amt Ccy="CHF">10.00</Amt>
                        <CdtDbtInd>CRDT</CdtDbtInd>
                        <AcctSvcrRef>REF666</AcctSvcrRef>
                    </Ntry>
                </Stmt>
            </BkToCstmrStmt>
        </Document>
        """
        parser = Camt053Parser(xml_data)
        transactions = parser.get_transactions()

        assert len(transactions) == 1
        assert transactions[0]["AccountIBAN"] is None

    def test_realistic_batch_of_entries_with_and_without_acctsvcrref(self):
        """End-to-end reproduction of the real file pattern: a mix of
        normal entries (with AcctSvcrRef) and interest/adjustment entries
        (without). All must be parsed without any exception, and the count
        of returned transactions must match the number of Ntry elements."""
        normal_entry = """
        <Ntry>
            <Amt Ccy="CHF">1054.75</Amt>
            <CdtDbtInd>CRDT</CdtDbtInd>
            <AcctSvcrRef>ZV20250101/000001</AcctSvcrRef>
            <BookgDt><Dt>2025-01-01</Dt></BookgDt>
            <ValDt><Dt>2025-01-01</Dt></ValDt>
        </Ntry>
        """
        interest_entry_no_ref = """
        <Ntry>
            <Amt Ccy="CHF">.02</Amt>
            <CdtDbtInd>CRDT</CdtDbtInd>
            <BookgDt><Dt>2025-12-31</Dt></BookgDt>
            <ValDt><Dt>2025-12-31</Dt></ValDt>
            <NtryDtls>
                <TxDtls>
                    <Refs>
                        <InstrId>NOTPROVIDED</InstrId>
                        <EndToEndId>NOTPROVIDED</EndToEndId>
                    </Refs>
                    <Amt Ccy="CHF">.02</Amt>
                    <CdtDbtInd>CRDT</CdtDbtInd>
                </TxDtls>
            </NtryDtls>
        </Ntry>
        """
        xml_data = _wrap(normal_entry + interest_entry_no_ref)
        parser = Camt053Parser(xml_data)

        transactions = parser.get_transactions()

        assert len(transactions) == 2
        by_amount = {tx["Amount"]: tx for tx in transactions}
        assert by_amount["1054.75"]["TransactionID"] == "ZV20250101/000001"
        assert by_amount[".02"]["TransactionID"] is None


class TestBalanceConsistency:
    """End-to-end sanity check reproducing the user's cumsum() bug report:
    sum(CRDT) - sum(DBIT) over all transactions of a statement must equal
    ClosingBalance - OpeningBalance. If the parser drops some entries (e.g.
    batch-only credits), this invariant breaks and the running balance
    plotted by the user drifts away from reality.
    """

    def test_crdt_minus_dbit_matches_balance_delta(self):
        entries_xml = (
            TestBatchOnlyEntry()._entry_xml(amount="88000.00", indicator="CRDT")
            + """
            <Ntry>
                <Amt Ccy="CHF">84000.00</Amt>
                <CdtDbtInd>DBIT</CdtDbtInd>
                <BookgDt><Dt>2021-05-15</Dt></BookgDt>
                <ValDt><Dt>2021-05-15</Dt></ValDt>
                <AcctSvcrRef>RENT001</AcctSvcrRef>
                <NtryDtls>
                    <TxDtls>
                        <Refs><EndToEndId>E2E-RENT</EndToEndId></Refs>
                        <Amt Ccy="CHF">84000.00</Amt>
                        <CdtDbtInd>DBIT</CdtDbtInd>
                    </TxDtls>
                </NtryDtls>
            </Ntry>
            """
        )
        xml_data = _wrap(entries_xml)
        parser = Camt053Parser(xml_data)

        transactions = parser.get_transactions()
        statement_info = parser.get_statement_info()[0]

        total_crdt = sum(float(tx["Amount"]) for tx in transactions if tx["CreditDebitIndicator"] == "CRDT")
        total_dbit = sum(float(tx["Amount"]) for tx in transactions if tx["CreditDebitIndicator"] == "DBIT")

        opening_balance = float(statement_info["OpeningBalance"])
        closing_balance = float(statement_info["ClosingBalance"])

        assert total_crdt - total_dbit == closing_balance - opening_balance
