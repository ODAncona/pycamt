import pytest

from pycamt.parser import Camt053ParseError, Camt053Parser

XML_DATA_STMT = """
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02">
    <BkToCstmrStmt>
        <GrpHdr>
            <MsgId>ABC123</MsgId>
            <CreDtTm>2020-06-23T18:56:25.64Z</CreDtTm>
        </GrpHdr>
        <Stmt>
            <Acct>
                <Id>
                    <IBAN>GB33BUKB20201555555555</IBAN>
                </Id>
            </Acct>
            <Bal>
                <Tp>
                    <CdOrPrtry>
                        <Cd>OPBD</Cd>
                    </CdOrPrtry>
                </Tp>
                <Dt>
                    <Dt>2025-07-31</Dt>
                </Dt>
                <Amt Ccy="EUR">1000.00</Amt>
            </Bal>
            <Ntry>
                <Amt Ccy="EUR">500.00</Amt>
                <CdtDbtInd>CRDT</CdtDbtInd>
                <BookgDt>
                    <Dt>2020-06-23</Dt>
                </BookgDt>
                <ValDt>
                    <Dt>2020-06-23</Dt>
                </ValDt>
                <AcctSvcrRef>123</AcctSvcrRef>
                <NtryDtls>
                    <TxDtls>
                        <Refs>
                            <EndToEndId>ENDTOENDID123</EndToEndId>
                        </Refs>
                        <AmtDtls>
                            <TxAmt>
                                <Amt Ccy="EUR">500.00</Amt>
                            </TxAmt>
                        </AmtDtls>
                    </TxDtls>
                </NtryDtls>
            </Ntry>
        </Stmt>
    </BkToCstmrStmt>
</Document>
"""

XML_DATA_RPT = """
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.052.001.08" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:iso:std:iso:20022:tech:xsd:camt.052.001.08 camt.052.001.08.xsd">
    <BkToCstmrAcctRpt>
        <GrpHdr>
            <MsgId>ABC123</MsgId>
            <CreDtTm>2020-06-23T18:56:25.64Z</CreDtTm>
        </GrpHdr>
        <Rpt>
            <Acct>
                <Id>
                    <IBAN>GB33BUKB20201555555555</IBAN>
                </Id>
            </Acct>
            <Bal>
                <Tp>
                    <CdOrPrtry>
                        <Cd>OPBD</Cd>
                    </CdOrPrtry>
                </Tp>
                <Dt>
                    <Dt>2025-07-31</Dt>
                </Dt>
                <Amt Ccy="EUR">1000.00</Amt>
            </Bal>
            <Ntry>
                <Amt Ccy="EUR">500.00</Amt>
                <CdtDbtInd>CRDT</CdtDbtInd>
                <Sts>
                    <Cd>BOOK</Cd>
                </Sts>
                <BookgDt>
                    <Dt>2020-06-23</Dt>
                </BookgDt>
                <ValDt>
                    <Dt>2020-06-23</Dt>
                </ValDt>
                <AcctSvcrRef>123</AcctSvcrRef>
                <NtryDtls>
                    <TxDtls>
                        <Refs>
                            <EndToEndId>ENDTOENDID123</EndToEndId>
                        </Refs>
                        <Amt Ccy="EUR">500.00</Amt>
                    </TxDtls>
                </NtryDtls>
            </Ntry>
        </Rpt>
    </BkToCstmrAcctRpt>
</Document>
"""


def pytest_generate_tests(metafunc):
    if "parser" in metafunc.fixturenames:
        metafunc.parametrize("parser", ["parser_stmt", "parser_rpt"], indirect=True)


@pytest.fixture
def parser(request):
    if request.param == "parser_stmt":
        return Camt053Parser(XML_DATA_STMT)
    if request.param == "parser_rpt":
        return Camt053Parser(XML_DATA_RPT)
    raise AssertionError("invalid internal test config")


class TestCamt053Parser:
    def test_get_group_header(self, parser):
        expected = {
            "MessageID": "ABC123",
            "CreationDateTime": "2020-06-23T18:56:25.64Z",
        }
        assert parser.get_group_header() == expected

    def test_get_transactions(self, parser):
        transactions = parser.get_transactions()
        assert len(transactions) > 0  # Ensure there's at least one transaction
        transaction = transactions[0]  # Access the first transaction

        assert transaction["Amount"] == "500.00"
        assert transaction["Currency"] == "EUR"
        assert transaction["CreditDebitIndicator"] == "CRDT"
        assert transaction["BookingDate"] == "2020-06-23"
        assert transaction["ValueDate"] == "2020-06-23"

    def test_get_statement_info(self, parser):
        expected = [
            {
                "IBAN": "GB33BUKB20201555555555",
                "OpeningBalance": "1000.00",
                "Currency": None,
                "ClosingBalance": None,
                "OpeningBalanceDate": "2025-07-31",
                "ClosingBalanceDate": None,
            }
        ]
        assert parser.get_statement_info() == expected

    def test_multiple_remittance_information(self):
        """Test that multiple Ustrd elements in RemittanceInformation are captured"""
        xml_data = """
        <Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02">
            <BkToCstmrStmt>
                <GrpHdr>
                    <MsgId>ABC123</MsgId>
                    <CreDtTm>2020-06-23T18:56:25.64Z</CreDtTm>
                </GrpHdr>
                <Stmt>
                    <Acct>
                        <Id>
                            <IBAN>GB33BUKB20201555555555</IBAN>
                        </Id>
                    </Acct>
                    <Ntry>
                        <Amt Ccy="EUR">69.06</Amt>
                        <CdtDbtInd>CRDT</CdtDbtInd>
                        <BookgDt>
                            <Dt>2020-07-07</Dt>
                        </BookgDt>
                        <ValDt>
                            <Dt>2020-07-07</Dt>
                        </ValDt>
                        <AcctSvcrRef>123</AcctSvcrRef>
                        <NtryDtls>
                            <TxDtls>
                                <Refs>
                                    <EndToEndId>ENDTOENDID123</EndToEndId>
                                </Refs>
                                <RmtInf>
                                    <Ustrd>Ref..      1234567890123456</Ustrd>
                                    <Ustrd>Betrag EUR            69,06</Ustrd>
                                    <Ustrd>/ADRS CH/Basel,1234</Ustrd>
                                    <Ustrd>  A12345/ Best 00123456</Ustrd>
                                    <Ustrd>7185) Peter Pan</Ustrd>
                                    <Ustrd>Urspr. EUR            69,06</Ustrd>
                                    <Ustrd>ADRS Re xxxxx,4 CH/Basel</Ustrd>
                                    <Ustrd>Land,1234/</Ustrd>
                                    <Ustrd>ERST RAIFCH12345</Ustrd>
                                </RmtInf>
                            </TxDtls>
                        </NtryDtls>
                    </Ntry>
                </Stmt>
            </BkToCstmrStmt>
        </Document>
        """
        parser = Camt053Parser(xml_data)
        transactions = parser.get_transactions()

        assert len(transactions) == 1
        transaction = transactions[0]

        # Current behavior: only first Ustrd element
        assert transaction["RemittanceInformation"] == "Ref..      1234567890123456"

        # New behavior: all Ustrd elements joined
        expected_full = (
            "Ref..      1234567890123456 Betrag EUR            69,06 "
            "/ADRS CH/Basel,1234 A12345/ Best 00123456 7185) Peter Pan "
            "Urspr. EUR            69,06 ADRS Re xxxxx,4 CH/Basel "
            "Land,1234/ ERST RAIFCH12345"
        )
        assert "RemittanceInformationFull" in transaction
        assert transaction["RemittanceInformationFull"] == expected_full

    def test_single_remittance_information_backward_compatibility(self):
        """Test that single Ustrd element works for both fields"""
        xml_data = """
        <Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02">
            <BkToCstmrStmt>
                <GrpHdr>
                    <MsgId>ABC123</MsgId>
                    <CreDtTm>2020-06-23T18:56:25.64Z</CreDtTm>
                </GrpHdr>
                <Stmt>
                    <Acct>
                        <Id>
                            <IBAN>GB33BUKB20201555555555</IBAN>
                        </Id>
                    </Acct>
                    <Ntry>
                        <Amt Ccy="EUR">500.00</Amt>
                        <CdtDbtInd>CRDT</CdtDbtInd>
                        <BookgDt>
                            <Dt>2020-06-23</Dt>
                        </BookgDt>
                        <ValDt>
                            <Dt>2020-06-23</Dt>
                        </ValDt>
                        <AcctSvcrRef>123</AcctSvcrRef>
                        <NtryDtls>
                            <TxDtls>
                                <Refs>
                                    <EndToEndId>ENDTOENDID123</EndToEndId>
                                </Refs>
                                <RmtInf>
                                    <Ustrd>Single remittance info</Ustrd>
                                </RmtInf>
                            </TxDtls>
                        </NtryDtls>
                    </Ntry>
                </Stmt>
            </BkToCstmrStmt>
        </Document>
        """
        parser = Camt053Parser(xml_data)
        transactions = parser.get_transactions()

        assert len(transactions) == 1
        transaction = transactions[0]

        # Both fields should have the same value for single Ustrd
        assert transaction["RemittanceInformation"] == "Single remittance info"
        assert transaction["RemittanceInformationFull"] == "Single remittance info"

    def test_no_remittance_information(self):
        """Test that transactions without RemittanceInformation still work"""
        xml_data = """
        <Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02">
            <BkToCstmrStmt>
                <GrpHdr>
                    <MsgId>ABC123</MsgId>
                    <CreDtTm>2020-06-23T18:56:25.64Z</CreDtTm>
                </GrpHdr>
                <Stmt>
                    <Acct>
                        <Id>
                            <IBAN>GB33BUKB20201555555555</IBAN>
                        </Id>
                    </Acct>
                    <Ntry>
                        <Amt Ccy="EUR">500.00</Amt>
                        <CdtDbtInd>CRDT</CdtDbtInd>
                        <BookgDt>
                            <Dt>2020-06-23</Dt>
                        </BookgDt>
                        <ValDt>
                            <Dt>2020-06-23</Dt>
                        </ValDt>
                        <AcctSvcrRef>123</AcctSvcrRef>
                        <NtryDtls>
                            <TxDtls>
                                <Refs>
                                    <EndToEndId>ENDTOENDID123</EndToEndId>
                                </Refs>
                            </TxDtls>
                        </NtryDtls>
                    </Ntry>
                </Stmt>
            </BkToCstmrStmt>
        </Document>
        """
        parser = Camt053Parser(xml_data)
        transactions = parser.get_transactions()

        assert len(transactions) == 1
        transaction = transactions[0]

        # Both fields should be None when no remittance info exists
        assert "RemittanceInformation" not in transaction  # Filtered out by return statement
        assert "RemittanceInformationFull" not in transaction  # Filtered out by return statement

    def test_structured_remittance_information(self):
        """Test that structured remittance data (Strd/CdtrRefInf/Ref) is parsed.

        Swiss QR-bills typically use <Strd> instead of <Ustrd>, this is a
        very common case for salary/rent payments and must not be silently
        dropped.
        """
        xml_data = """
        <Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02">
            <BkToCstmrStmt>
                <GrpHdr>
                    <MsgId>ABC123</MsgId>
                    <CreDtTm>2020-06-23T18:56:25.64Z</CreDtTm>
                </GrpHdr>
                <Stmt>
                    <Acct>
                        <Id>
                            <IBAN>CH9300762011623852957</IBAN>
                        </Id>
                    </Acct>
                    <Ntry>
                        <Amt Ccy="CHF">88000.00</Amt>
                        <CdtDbtInd>CRDT</CdtDbtInd>
                        <BookgDt>
                            <Dt>2021-05-01</Dt>
                        </BookgDt>
                        <ValDt>
                            <Dt>2021-05-01</Dt>
                        </ValDt>
                        <AcctSvcrRef>QR001</AcctSvcrRef>
                        <NtryDtls>
                            <TxDtls>
                                <Refs>
                                    <EndToEndId>ENDTOENDID999</EndToEndId>
                                </Refs>
                                <RmtInf>
                                    <Strd>
                                        <CdtrRefInf>
                                            <Ref>210000000003139471430009017</Ref>
                                        </CdtrRefInf>
                                        <AddtlRmtInf>Salaire mai 2021</AddtlRmtInf>
                                    </Strd>
                                </RmtInf>
                            </TxDtls>
                        </NtryDtls>
                    </Ntry>
                </Stmt>
            </BkToCstmrStmt>
        </Document>
        """
        parser = Camt053Parser(xml_data)
        transactions = parser.get_transactions()

        assert len(transactions) == 1
        transaction = transactions[0]

        assert transaction["Amount"] == "88000.00"
        assert transaction["CreditDebitIndicator"] == "CRDT"
        assert transaction["RemittanceInformation"] == "210000000003139471430009017"
        assert transaction["AdditionalRemittanceInformation"] == "Salaire mai 2021"


class TestCamt053ParserErrors:
    """Tests for error handling and edge cases that are not covered by the
    parametrized 'parser' fixture."""

    def test_from_file(self, tmp_path):
        file_path = tmp_path / "statement.xml"
        file_path.write_text(XML_DATA_STMT, encoding="utf-8")

        parser = Camt053Parser.from_file(file_path)

        assert parser.get_group_header() == {
            "MessageID": "ABC123",
            "CreationDateTime": "2020-06-23T18:56:25.64Z",
        }
        transactions = parser.get_transactions()
        assert len(transactions) == 1

    def test_from_file_accepts_str_path(self, tmp_path):
        file_path = tmp_path / "statement.xml"
        file_path.write_text(XML_DATA_STMT, encoding="utf-8")

        parser = Camt053Parser.from_file(str(file_path))

        assert len(parser.get_transactions()) == 1

    def test_missing_stmt_and_rpt_raises(self):
        """A document without any Stmt or Rpt element must raise loudly
        instead of silently returning an empty list of transactions."""
        xml_data = """
        <Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02">
            <BkToCstmrStmt>
                <GrpHdr>
                    <MsgId>ABC123</MsgId>
                    <CreDtTm>2020-06-23T18:56:25.64Z</CreDtTm>
                </GrpHdr>
            </BkToCstmrStmt>
        </Document>
        """
        parser = Camt053Parser(xml_data)

        with pytest.raises(Camt053ParseError):
            parser.get_transactions()

        with pytest.raises(Camt053ParseError):
            parser.get_statement_info()

    def test_get_group_header_missing_returns_empty_dict(self):
        xml_data = """
        <Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02">
            <BkToCstmrStmt>
                <Stmt>
                    <Acct>
                        <Id>
                            <IBAN>GB33BUKB20201555555555</IBAN>
                        </Id>
                    </Acct>
                </Stmt>
            </BkToCstmrStmt>
        </Document>
        """
        parser = Camt053Parser(xml_data)
        assert parser.get_group_header() == {}

    @pytest.mark.parametrize(
        ("namespace", "expected_version"),
        [
            ("urn:iso:std:iso:20022:tech:xsd:camt.053.001.02", "camt.053.001.02"),
            ("urn:iso:std:iso:20022:tech:xsd:camt.053.001.03", "camt.053.001.03"),
            ("urn:iso:std:iso:20022:tech:xsd:camt.053.001.04", "camt.053.001.04"),
            ("urn:iso:std:iso:20022:tech:xsd:camt.053.001.08", "camt.053.001.08"),
            ("urn:iso:std:iso:20022:tech:xsd:camt.053.001.12", "camt.053.001.12"),
            ("urn:iso:std:iso:20022:tech:xsd:camt.054.001.02", "unknown"),
        ],
    )
    def test_detect_version(self, namespace, expected_version):
        xml_data = f"""
        <Document xmlns="{namespace}">
            <BkToCstmrStmt>
                <GrpHdr>
                    <MsgId>ABC123</MsgId>
                    <CreDtTm>2020-06-23T18:56:25.64Z</CreDtTm>
                </GrpHdr>
                <Stmt>
                    <Acct>
                        <Id>
                            <IBAN>GB33BUKB20201555555555</IBAN>
                        </Id>
                    </Acct>
                </Stmt>
            </BkToCstmrStmt>
        </Document>
        """
        parser = Camt053Parser(xml_data)
        assert parser.version == expected_version


class TestGetStatementInfoBalances:
    """Tests covering closing balance, date/time variants and DBIT sign
    handling in get_statement_info(), which were previously untested."""

    def _make_xml(self, opbd_amt, opbd_ind, clbd_amt, clbd_ind, use_dttm=False):
        opbd_date = "<DtTm>2025-06-30T00:00:00</DtTm>" if use_dttm else "<Dt>2025-06-30</Dt>"
        clbd_date = "<DtTm>2025-07-31T00:00:00</DtTm>" if use_dttm else "<Dt>2025-07-31</Dt>"
        return f"""
        <Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02">
            <BkToCstmrStmt>
                <GrpHdr>
                    <MsgId>ABC123</MsgId>
                    <CreDtTm>2020-06-23T18:56:25.64Z</CreDtTm>
                </GrpHdr>
                <Stmt>
                    <Acct>
                        <Id>
                            <IBAN>CH9300762011623852957</IBAN>
                        </Id>
                        <Ccy>CHF</Ccy>
                    </Acct>
                    <Bal>
                        <Tp>
                            <CdOrPrtry>
                                <Cd>OPBD</Cd>
                            </CdOrPrtry>
                        </Tp>
                        <Dt>{opbd_date}</Dt>
                        <Amt Ccy="CHF">{opbd_amt}</Amt>
                        <CdtDbtInd>{opbd_ind}</CdtDbtInd>
                    </Bal>
                    <Bal>
                        <Tp>
                            <CdOrPrtry>
                                <Cd>CLBD</Cd>
                            </CdOrPrtry>
                        </Tp>
                        <Dt>{clbd_date}</Dt>
                        <Amt Ccy="CHF">{clbd_amt}</Amt>
                        <CdtDbtInd>{clbd_ind}</CdtDbtInd>
                    </Bal>
                </Stmt>
            </BkToCstmrStmt>
        </Document>
        """

    def test_closing_balance_credit(self):
        xml_data = self._make_xml("1000.00", "CRDT", "4000.00", "CRDT")
        parser = Camt053Parser(xml_data)
        info = parser.get_statement_info()[0]

        assert info["OpeningBalance"] == "1000.00"
        assert info["ClosingBalance"] == "4000.00"
        assert info["ClosingBalanceDate"] == "2025-07-31"

    def test_closing_balance_debit_sign_is_flipped(self):
        """A DBIT closing balance (account overdrawn) should be represented
        as a negative number, not a positive one."""
        xml_data = self._make_xml("1000.00", "CRDT", "84000.00", "DBIT")
        parser = Camt053Parser(xml_data)
        info = parser.get_statement_info()[0]

        assert info["ClosingBalance"] == "-84000.0"

    def test_opening_balance_debit_sign_is_flipped(self):
        xml_data = self._make_xml("500.00", "DBIT", "1000.00", "CRDT")
        parser = Camt053Parser(xml_data)
        info = parser.get_statement_info()[0]

        assert info["OpeningBalance"] == "-500.0"

    def test_balance_date_time_variant(self):
        """Some banks report Dt/DtTm instead of Dt/Dt for balance dates."""
        xml_data = self._make_xml("1000.00", "CRDT", "4000.00", "CRDT", use_dttm=True)
        parser = Camt053Parser(xml_data)
        info = parser.get_statement_info()[0]

        assert info["OpeningBalanceDate"] == "2025-06-30T00:00:00"
        assert info["ClosingBalanceDate"] == "2025-07-31T00:00:00"

    def test_multi_statement_document(self):
        """A single CAMT.053 file can contain several Stmt blocks (e.g. one
        per account). Each one should be reported independently."""
        xml_data = """
        <Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.02">
            <BkToCstmrStmt>
                <GrpHdr>
                    <MsgId>ABC123</MsgId>
                    <CreDtTm>2020-06-23T18:56:25.64Z</CreDtTm>
                </GrpHdr>
                <Stmt>
                    <Acct>
                        <Id><IBAN>CH1111111111111111111</IBAN></Id>
                    </Acct>
                    <Bal>
                        <Tp><CdOrPrtry><Cd>OPBD</Cd></CdOrPrtry></Tp>
                        <Dt><Dt>2025-06-30</Dt></Dt>
                        <Amt Ccy="CHF">100.00</Amt>
                        <CdtDbtInd>CRDT</CdtDbtInd>
                    </Bal>
                </Stmt>
                <Stmt>
                    <Acct>
                        <Id><IBAN>CH2222222222222222222</IBAN></Id>
                    </Acct>
                    <Bal>
                        <Tp><CdOrPrtry><Cd>OPBD</Cd></CdOrPrtry></Tp>
                        <Dt><Dt>2025-06-30</Dt></Dt>
                        <Amt Ccy="CHF">200.00</Amt>
                        <CdtDbtInd>CRDT</CdtDbtInd>
                    </Bal>
                </Stmt>
            </BkToCstmrStmt>
        </Document>
        """
        parser = Camt053Parser(xml_data)
        statements = parser.get_statement_info()

        assert len(statements) == 2
        assert statements[0]["IBAN"] == "CH1111111111111111111"
        assert statements[0]["OpeningBalance"] == "100.00"
        assert statements[1]["IBAN"] == "CH2222222222222222222"
        assert statements[1]["OpeningBalance"] == "200.00"
