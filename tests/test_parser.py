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
