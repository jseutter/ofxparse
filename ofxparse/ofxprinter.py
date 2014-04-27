class OfxPrinter():
    ofx = None

    def __init__(self, ofx):
        self.ofx = ofx

    def writeHeaders(self, ofh):
        for k, v in self.ofx.headers.iteritems():
            if v is None:
                ofh.write("{0}:NONE\r\n".format(k, v))
            else:
                ofh.write("{0}:{1}\r\n".format(k, v))
        ofh.write("\r\n")

    def writeSignOn(self, ofh):
        ofh.write(self.ofx.signon.__str__())

    def printDate(self, dt, msec_digs=3):
        strdt = dt.strftime('%Y%m%d%H%M%S')
        strdt_msec = dt.strftime('%f')
        if len(strdt_msec) < msec_digs:
            strdt_msec += ('0' * (msec_digs - len(strdt_msec)))
        elif len(strdt_msec) > msec_digs:
            strdt_msec = strdt_msec[:msec_digs]
        return strdt + '.' + strdt_msec

    def writeTrn(self, ofh, trn):
        ofh.write("\t\t\t\t\t<STMTTRN>\r\n")
        ofh.write("\t\t\t\t\t\t<TRNTYPE>{}\r\n".format(
            trn.type.upper()
        ))
        ofh.write("\t\t\t\t\t\t<DTPOSTED>{}\r\n".format(
            self.printDate(trn.date)
        ))
        ofh.write("\t\t\t\t\t\t<TRNAMT>{0:.2f}\r\n".format(
            float(trn.amount)
        ))

        ofh.write("\t\t\t\t\t\t<FITID>{}\r\n".format(
            trn.id
        ))

        if trn.checknum:
            ofh.write("\t\t\t\t\t\t<CHECKNUM>{}\r\n".format(
                trn.checknum
            ))

        ofh.write("\t\t\t\t\t\t<NAME>{}\r\n".format(
            trn.payee
        ))

        if trn.memo.strip():
            ofh.write("\t\t\t\t\t\t<MEMO>{}\r\n".format(
                trn.memo
            ))

        ofh.write("\t\t\t\t\t</STMTTRN>\r\n")

    def writeLedgerBal(self, ofh, statement):
        bal = getattr(statement, 'balance')
        baldt = getattr(statement, 'balance_date')

        if bal and baldt:
            ofh.write("\t\t\t\t<LEDGERBAL>\r\n")
            ofh.write("\t\t\t\t\t<BALAMT>{0:.2f}\r\n".format(
                float(bal)
            ))
            ofh.write("\t\t\t\t\t<DTASOF>{0}\r\n".format(
                self.printDate(baldt)
            ))
            ofh.write("\t\t\t\t</LEDGERBAL>\r\n")

    def writeAvailBal(self, ofh, statement):
        bal = getattr(statement, 'available_balance')
        baldt = getattr(statement, 'available_balance_date')

        if bal and baldt:
            ofh.write("\t\t\t\t<AVAILBAL>\r\n")
            ofh.write("\t\t\t\t\t<BALAMT>{0:.2f}\r\n".format(
                float(bal)
            ))
            ofh.write("\t\t\t\t\t<DTASOF>{0}\r\n".format(
                self.printDate(baldt)
            ))
            ofh.write("\t\t\t\t</AVAILBAL>\r\n")

    def writeStmTrs(self, ofh):
        for acct in self.ofx.accounts:
            ofh.write("\t\t\t<STMTRS>\r\n")

            if acct.curdef:
                ofh.write("\t\t\t\t<CURDEF>{0}\r\n".format(
                    acct.curdef
                ))

            if acct.routing_number or acct.account_id or acct.account_type:
                ofh.write("\t\t\t\t<BANKACCTFROM>\r\n")
                if acct.routing_number:
                    ofh.write("\t\t\t\t\t<BANKID>{0}\r\n".format(
                        acct.routing_number
                    ))
                if acct.account_id:
                    ofh.write("\t\t\t\t\t<ACCTID>{0}\r\n".format(
                        acct.account_id
                    ))
                if acct.account_type:
                    ofh.write("\t\t\t\t\t<ACCTTYPE>{0}\r\n".format(
                        acct.account_type
                    ))
                ofh.write("\t\t\t\t</BANKACCTFROM>\r\n")

            ofh.write("\t\t\t\t<BANKTRANLIST>\r\n")
            ofh.write("\t\t\t\t\t<DTSTART>{0}\r\n".format(
                self.printDate(acct.statement.start_date)
            ))
            ofh.write("\t\t\t\t\t<DTEND>{0}\r\n".format(
                self.printDate(acct.statement.end_date)
            ))

            for trn in acct.statement.transactions:
                self.writeTrn(ofh, trn)

            ofh.write("\t\t\t\t</BANKTRANLIST>\r\n")

            self.writeLedgerBal(ofh, acct.statement)
            self.writeAvailBal(ofh, acct.statement)

            ofh.write("\t\t\t</STMTRS>\r\n")

    def writeBankMsgsRsv1(self, ofh):
        ofh.write("\t<BANKMSGSRSV1>\r\n")
        ofh.write("\t\t<STMTTRNRS>\r\n")
        if self.ofx.trnuid is not None:
            ofh.write("\t\t\t<TRNUID>{0}\r\n".format(
                self.ofx.trnuid
            ))
        if self.ofx.status:
            ofh.write("\t\t\t<STATUS>\r\n")
            ofh.write("\t\t\t\t<CODE>{0}\r\n".format(
                self.ofx.status['code']
            ))
            ofh.write("\t\t\t\t<SEVERITY>{0}\r\n".format(
                self.ofx.status['severity']
            ))
            ofh.write("\t\t\t</STATUS>\r\n")
        self.writeStmTrs(ofh)
        ofh.write("\t\t</STMTTRNRS>\r\n")
        ofh.write("\t</BANKMSGSRSV1>\r\n")

    def writeOfx(self, ofh):
        ofh.write("<OFX>\r\n")
        self.writeSignOn(ofh)
        self.writeBankMsgsRsv1(ofh)
        ofh.write("</OFX>\r\n")

    def write(self, outfilename):
        outfile = open(outfilename, 'wb')
        self.writeHeaders(outfile)
        self.writeOfx(outfile)
        outfile.flush()
        outfile.close()
