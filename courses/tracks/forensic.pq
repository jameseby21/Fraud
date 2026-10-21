let
    Read = (FileName as text) as table =>
        let
            Allowed = {"payments.csv", "entities.csv", "invoices.csv", "bank_entries.csv"},
            Content = if List.Contains(Allowed, FileName) then File.Contents(CaseFolder & "/" & FileName) else error "Unknown case file",
            CSV = Csv.Document(Content, [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
            Headers = Table.PromoteHeaders(CSV, [PromoteAllScalars=true]),
            NumberTypes = {{"amount_cents", Int64.Type}, {"invoice_amount_cents", Int64.Type}, {"signed_amount_cents", Int64.Type}, {"payment_terms_days", Int64.Type}},
            ExistingNumbers = List.Select(NumberTypes, each List.Contains(Table.ColumnNames(Headers), _{0})),
            Typed = Table.TransformColumnTypes(Headers, ExistingNumbers),
            DateNames = List.Intersect({Table.ColumnNames(Typed), {"invoice_date", "payment_date", "posted_date", "available_on"}}),
            Dates = Table.TransformColumns(Typed, List.Transform(DateNames, (Name) => {Name, each Date.FromText(_, [Format="yyyy-MM-dd", Culture="en-US"]), type date}))
        in Dates
in
    [Payments=Read("payments.csv"), Entities=Read("entities.csv"), Invoices=Read("invoices.csv"), BankEntries=Read("bank_entries.csv")]
