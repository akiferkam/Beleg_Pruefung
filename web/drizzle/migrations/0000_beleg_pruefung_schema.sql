CREATE TABLE public.batches (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  is_sample boolean NOT NULL DEFAULT false,
  created_by uuid,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE public.documents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  batch_id uuid NOT NULL REFERENCES public.batches(id) ON DELETE CASCADE,
  doc_id text NOT NULL,
  file_name text NOT NULL,
  storage_path text NOT NULL,
  mime_type text,
  file_hash text NOT NULL,
  page_count integer NOT NULL DEFAULT 0,
  text_layer text NOT NULL DEFAULT '',
  readable boolean NOT NULL DEFAULT true,
  intake_error text,
  extraction jsonb,
  extraction_error text,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX documents_batch_idx ON public.documents(batch_id);
CREATE TABLE public.orders (
  bestellnummer text PRIMARY KEY,
  lieferant text NOT NULL,
  artikel text NOT NULL,
  menge numeric NOT NULL,
  einzelpreis_netto numeric NOT NULL
);
CREATE TABLE public.ledger_entries (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid,
  doc_id text NOT NULL,
  file_hash text NOT NULL,
  supplier_name text,
  invoice_number text,
  invoice_date text,
  order_reference text,
  net_amount numeric,
  gross_amount numeric,
  total_quantity numeric,
  line_items_fp text NOT NULL DEFAULT '',
  supplier_iban text,
  decision text,
  processed_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE public.overrides (
  document_id uuid PRIMARY KEY REFERENCES public.documents(id) ON DELETE CASCADE,
  entscheidung text NOT NULL,
  notiz text NOT NULL DEFAULT '',
  automatisch_war text NOT NULL DEFAULT '',
  user_id uuid,
  zeitpunkt timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE public.app_settings (
  id integer PRIMARY KEY DEFAULT 1,
  company jsonb NOT NULL,
  policy jsonb NOT NULL,
  updated_at timestamptz NOT NULL DEFAULT now()
);

GRANT SELECT, INSERT, UPDATE, DELETE ON public.batches, public.documents, public.orders, public.ledger_entries, public.overrides, public.app_settings TO authenticated;
GRANT ALL ON public.batches, public.documents, public.orders, public.ledger_entries, public.overrides, public.app_settings TO service_role;

ALTER TABLE public.batches ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ledger_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.overrides ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.app_settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "team access" ON public.batches FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "team access" ON public.documents FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "team access" ON public.orders FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "team access" ON public.ledger_entries FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "team access" ON public.overrides FOR ALL TO authenticated USING (true) WITH CHECK (true);
CREATE POLICY "team read" ON public.app_settings FOR SELECT TO authenticated USING (true);
CREATE POLICY "team update" ON public.app_settings FOR UPDATE TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "team read belege" ON storage.objects FOR SELECT TO authenticated USING (bucket_id = 'belege');
CREATE POLICY "team upload belege" ON storage.objects FOR INSERT TO authenticated WITH CHECK (bucket_id = 'belege');

INSERT INTO public.app_settings (id, company, policy) VALUES (1,
 '{"name":"Quellberg GmbH","address_contains":["Limonadenweg","94032 Passau"],"vat_id":"DE811907980"}'::jsonb,
 '{"extra_items_tolerance_pct":10,"no_po_match_means_hinschauen":true,"mandatory_review_amount_eur":50000,"line_arithmetic_tolerance_per_unit_eur":0.005,"net_sum_tolerance_eur":0.05,"vat_amount_tolerance_eur":0.02,"gross_amount_tolerance_eur":0.02,"valid_vat_rates_pct":[0,7,19],"grounding_enabled":true,"supplier_fuzzy_match_min_score":70}'::jsonb);