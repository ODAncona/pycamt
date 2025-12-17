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
      <FrToDt>
        <FrDtTm>2024-12-13T00:00:00</FrDtTm>
        <ToDtTm>2025-12-13T23:59:59</ToDtTm>
      </FrToDt>
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
      <Bal>
        <Tp>
          <CdOrPrtry>
            <Cd>OPBD</Cd>
          </CdOrPrtry>
        </Tp>
        <Amt Ccy="CHF">5950.8</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <Dt>
          <Dt>2024-12-15</Dt>
        </Dt>
      </Bal>
      <Bal>
        <Tp>
          <CdOrPrtry>
            <Cd>CLBD</Cd>
          </CdOrPrtry>
        </Tp>
        <Amt Ccy="CHF">4568.98</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <Dt>
          <Dt>2025-12-13</Dt>
        </Dt>
      </Bal>
      <TxsSummry>
        <TtlNtries>
          <NbOfNtries>174</NbOfNtries>
          <Sum>282567.72</Sum>
          <TtlNetNtry>
            <Amt>1381.82</Amt>
            <CdtDbtInd>DBIT</CdtDbtInd>
          </TtlNetNtry>
        </TtlNtries>
        <TtlCdtNtries>
          <NbOfNtries>33</NbOfNtries>
          <Sum>140592.95</Sum>
        </TtlCdtNtries>
        <TtlDbtNtries>
          <NbOfNtries>141</NbOfNtries>
          <Sum>141974.77</Sum>
        </TtlDbtNtries>
        <TtlNtriesPerBkTxCd>
          <NbOfNtries>2</NbOfNtries>
          <Sum>100</Sum>
          <TtlNetNtry>
            <Amt>100</Amt>
            <CdtDbtInd>CRDT</CdtDbtInd>
          </TtlNetNtry>
          <BkTxCd>
            <Domn>
              <Cd>PMNT</Cd>
              <Fmly>
                <Cd>ICDT</Cd>
                <SubFmlyCd>DAJT</SubFmlyCd>
              </Fmly>
            </Domn>
          </BkTxCd>
        </TtlNtriesPerBkTxCd>
        <TtlNtriesPerBkTxCd>
          <NbOfNtries>141</NbOfNtries>
          <Sum>141974.77</Sum>
          <TtlNetNtry>
            <Amt>141974.77</Amt>
            <CdtDbtInd>DBIT</CdtDbtInd>
          </TtlNetNtry>
          <BkTxCd>
            <Domn>
              <Cd>PMNT</Cd>
              <Fmly>
                <Cd>ICDT</Cd>
                <SubFmlyCd>OTHR</SubFmlyCd>
              </Fmly>
            </Domn>
          </BkTxCd>
        </TtlNtriesPerBkTxCd>
        <TtlNtriesPerBkTxCd>
          <NbOfNtries>29</NbOfNtries>
          <Sum>116207.75</Sum>
          <TtlNetNtry>
            <Amt>116207.75</Amt>
            <CdtDbtInd>CRDT</CdtDbtInd>
          </TtlNetNtry>
          <BkTxCd>
            <Domn>
              <Cd>PMNT</Cd>
              <Fmly>
                <Cd>RCDT</Cd>
                <SubFmlyCd>OTHR</SubFmlyCd>
              </Fmly>
            </Domn>
          </BkTxCd>
        </TtlNtriesPerBkTxCd>
        <TtlNtriesPerBkTxCd>
          <NbOfNtries>2</NbOfNtries>
          <Sum>24285.2</Sum>
          <TtlNetNtry>
            <Amt>24285.2</Amt>
            <CdtDbtInd>CRDT</CdtDbtInd>
          </TtlNetNtry>
          <BkTxCd>
            <Domn>
              <Cd>PMNT</Cd>
              <Fmly>
                <Cd>RCDT</Cd>
                <SubFmlyCd>SALA</SubFmlyCd>
              </Fmly>
            </Domn>
          </BkTxCd>
        </TtlNtriesPerBkTxCd>
      </TxsSummry>
      <Ntry>
        <Amt Ccy="CHF">16458.75</Amt>
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
            <TtlAmt Ccy="CHF">16458.75</TtlAmt>
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
        <AcctSvcrRef>ZV20251211/127310</AcctSvcrRef>
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
              <AcctSvcrRef>ZV20251211/127310/1</AcctSvcrRef>
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
              <Ustrd>10.12.2025 16:54 KTP AU, AU Kartennummer: 535222******8761 </Ustrd>
            </RmtInf>
            <AddtlTxInf>Einkauf Debitkarte 10.12.2025 16:54 KTP AU, AU Kartennummer: 535222******8761</AddtlTxInf>
          </TxDtls>
        </NtryDtls>
        <AddtlNtryInf>Einkauf Debitkarte 10.12.2025 16:54 KTP AU, AU Kartennummer: 535222******8761</AddtlNtryInf>
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

        assert transaction["Amount"] == "500.00"
        assert transaction["Currency"] == "CHF"
        assert transaction["CreditDebitIndicator"] == "CRDT"
        assert transaction["BookingDate"] == "2020-06-23"
        assert transaction["ValueDate"] == "2020-06-23"
