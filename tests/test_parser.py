import pytest

from pycamt.parser import Camt053Parser


@pytest.fixture
def parser():
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
    return Camt053Parser(xml_data)


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
