let
    Source = Csv.Document(File.Contents(FixturePath), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    TextAndMoney = Table.TransformColumnTypes(Headers, {
        {"transaction_id", type text}, {"invoice_id", type text}, {"supplier", type text},
        {"department", type text}, {"category", type text}, {"region", type text},
        {"currency", type text}, {"synthetic", type text}, {"amount_cents", Int64.Type}}),
    Dates = Table.TransformColumns(TextAndMoney, {
        {"invoice_date", each Date.FromText(_, [Format="yyyy-MM-dd", Culture="en-US"]), type date},
        {"payment_date", each Date.FromText(_, [Format="yyyy-MM-dd", Culture="en-US"]), type date}}),
    Amount = Table.AddColumn(Dates, "AmountUSD", each [amount_cents] / 100, Currency.Type),
    Delay = Table.AddColumn(Amount, "DelayDays", each Duration.Days([payment_date] - [invoice_date]), Int64.Type),
    Month = Table.AddColumn(Delay, "InvoiceMonth", each Date.StartOfMonth([invoice_date]), type date)
in
    Month
