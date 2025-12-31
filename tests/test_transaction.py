import pytest

from pycamt.parser import Camt053Parser


@pytest.fixture
def parser():
    xml_data = """
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.04">
  <BkToCstmrStmt>
    <GrpHdr>
      <MsgId>2025121402704522</MsgId>
      <CreDtTm>2025-12-14T18:33:53</CreDtTm>
      <MsgPgntn>
        <PgNb>1</PgNb>
        <LastPgInd>true</LastPgInd>
      </MsgPgntn>
    </GrpHdr>
    <Stmt>
      <Id>2025121402704522</Id>
      <ElctrncSeqNb>6</ElctrncSeqNb>
      <CreDtTm>2025-12-14T18:33:53</CreDtTm>
      <CpyDplctInd>DUPL</CpyDplctInd>
      <Acct>
        <Id>
          <IBAN>CH123456789</IBAN>
        </Id>
        <Ccy>CHF</Ccy>
        <Ownr>
          <Nm>Donald Duck</Nm>
          <PstlAdr>
            <AdrLine>Disney str</AdrLine>
            <AdrLine>123456 USA</AdrLine>
          </PstlAdr>
        </Ownr>
        <Svcr>
          <FinInstnId>
            <BICFI>ARBHCH22XXX</BICFI>
            <Nm>Picsou Bank AG</Nm>
          </FinInstnId>
        </Svcr>
      </Acct>

      <Ntry>
        <Amt Ccy="CHF">12345.678</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <RvslInd>false</RvslInd>
        <Sts>BOOK</Sts>
        <BookgDt>
          <Dt>2025-11-25</Dt>
        </BookgDt>
        <ValDt>
          <Dt>2025-11-25</Dt>
        </ValDt>
        <AcctSvcrRef>ZV20251125/001829</AcctSvcrRef>
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
            <NbOfTxs>1</NbOfTxs>
            <TtlAmt Ccy="CHF">12345.678</TtlAmt>
            <CdtDbtInd>CRDT</CdtDbtInd>
          </Btch>
        </NtryDtls>
        <AddtlNtryInf>Salär / Rente</AddtlNtryInf>
      </Ntry>
      <Ntry>
        <Amt Ccy="CHF">123.2</Amt>
        <CdtDbtInd>DBIT</CdtDbtInd>
        <RvslInd>false</RvslInd>
        <Sts>BOOK</Sts>
        <BookgDt>
          <Dt>2025-12-11</Dt>
        </BookgDt>
        <ValDt>
          <Dt>2025-12-10</Dt>
        </ValDt>
        <AcctSvcrRef>ZV20251201/127310</AcctSvcrRef>
        <BkTxCd>
          <Domn>
            <Cd>PMNT</Cd>
            <Fmly>
              <Cd>ICDT</Cd>
              <SubFmlyCd>OTHR</SubFmlyCd>
            </Fmly>
          </Domn>
        </BkTxCd>
        <NtryDtls>
          <Btch>
            <NbOfTxs>1</NbOfTxs>
            <TtlAmt Ccy="CHF">123.2</TtlAmt>
            <CdtDbtInd>DBIT</CdtDbtInd>
          </Btch>
          <TxDtls>
            <Refs>
              <AcctSvcrRef>ZV20251201/127310/1</AcctSvcrRef>
              <InstrId>0</InstrId>
              <EndToEndId>NOTPROVIDED</EndToEndId>
            </Refs>
            <Amt Ccy="CHF">123.2</Amt>
            <CdtDbtInd>DBIT</CdtDbtInd>
            <AmtDtls>
              <InstdAmt>
                <Amt Ccy="CHF">123.2</Amt>
              </InstdAmt>
            </AmtDtls>
            <RltdPties>
              <Dbtr>
                <Nm>NOTPROVIDED</Nm>
              </Dbtr>
              <Cdtr>
                <Nm>Donald Duck</Nm>
                <PstlAdr>
                  <AdrLine>Disney str</AdrLine>
                  <AdrLine>123456 USA</AdrLine>
                </PstlAdr>
              </Cdtr>
            </RltdPties>
            <RmtInf>
              <Ustrd>10.12.2025 16:00 Kartennummer: 1231456798 </Ustrd>
            </RmtInf>
            <AddtlTxInf>Einkauf Debitkarte 10.12.2025 16:00 Kartennummer: 1231456798</AddtlTxInf>
          </TxDtls>
        </NtryDtls>
        <AddtlNtryInf>Einkauf Debitkarte 10.12.2025 16:00 Kartennummer: 1231456798</AddtlNtryInf>
      </Ntry>
    </Stmt>
  </BkToCstmrStmt>
</Document>
    """
    return Camt053Parser(xml_data)


class TestTransactionCamt053Parser:
    def test_get_transactions(self, parser):
        transactions = parser.get_transactions()
        assert len(transactions) == 2
        transaction = transactions[0]  # Access the first transaction

        assert transaction["Amount"] == "12345.678"
        assert transaction["Currency"] == "CHF"
        assert transaction["CreditDebitIndicator"] == "CRDT"
        assert transaction["BookingDate"] == "2025-11-25"
        assert transaction["ValueDate"] == "2025-11-25"

        transaction = transactions[1]  # Access the 2nd transaction

        assert transaction["Amount"] == "123.2"
        assert transaction["Currency"] == "CHF"
        assert transaction["CreditDebitIndicator"] == "DBIT"
        assert transaction["BookingDate"] == "2025-12-11"
        assert transaction["ValueDate"] == "2025-12-10"
