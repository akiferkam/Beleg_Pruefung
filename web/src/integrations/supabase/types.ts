export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.18"
  }
  public: {
    Tables: {
      app_settings: {
        Row: {
          company: Json
          id: number
          policy: Json
          updated_at: string
        }
        Insert: {
          company: Json
          id?: number
          policy: Json
          updated_at?: string
        }
        Update: {
          company?: Json
          id?: number
          policy?: Json
          updated_at?: string
        }
        Relationships: []
      }
      batches: {
        Row: {
          created_at: string
          created_by: string | null
          id: string
          is_sample: boolean
          name: string
        }
        Insert: {
          created_at?: string
          created_by?: string | null
          id?: string
          is_sample?: boolean
          name: string
        }
        Update: {
          created_at?: string
          created_by?: string | null
          id?: string
          is_sample?: boolean
          name?: string
        }
        Relationships: []
      }
      documents: {
        Row: {
          batch_id: string
          created_at: string
          doc_id: string
          extraction: Json | null
          extraction_error: string | null
          file_hash: string
          file_name: string
          id: string
          intake_error: string | null
          mime_type: string | null
          page_count: number
          readable: boolean
          storage_path: string
          text_layer: string
        }
        Insert: {
          batch_id: string
          created_at?: string
          doc_id: string
          extraction?: Json | null
          extraction_error?: string | null
          file_hash: string
          file_name: string
          id?: string
          intake_error?: string | null
          mime_type?: string | null
          page_count?: number
          readable?: boolean
          storage_path: string
          text_layer?: string
        }
        Update: {
          batch_id?: string
          created_at?: string
          doc_id?: string
          extraction?: Json | null
          extraction_error?: string | null
          file_hash?: string
          file_name?: string
          id?: string
          intake_error?: string | null
          mime_type?: string | null
          page_count?: number
          readable?: boolean
          storage_path?: string
          text_layer?: string
        }
        Relationships: [
          {
            foreignKeyName: "documents_batch_id_fkey"
            columns: ["batch_id"]
            isOneToOne: false
            referencedRelation: "batches"
            referencedColumns: ["id"]
          },
        ]
      }
      ledger_entries: {
        Row: {
          decision: string | null
          doc_id: string
          document_id: string | null
          file_hash: string
          gross_amount: number | null
          id: string
          invoice_date: string | null
          invoice_number: string | null
          line_items_fp: string
          net_amount: number | null
          order_reference: string | null
          processed_at: string
          supplier_iban: string | null
          supplier_name: string | null
          total_quantity: number | null
        }
        Insert: {
          decision?: string | null
          doc_id: string
          document_id?: string | null
          file_hash: string
          gross_amount?: number | null
          id?: string
          invoice_date?: string | null
          invoice_number?: string | null
          line_items_fp?: string
          net_amount?: number | null
          order_reference?: string | null
          processed_at?: string
          supplier_iban?: string | null
          supplier_name?: string | null
          total_quantity?: number | null
        }
        Update: {
          decision?: string | null
          doc_id?: string
          document_id?: string | null
          file_hash?: string
          gross_amount?: number | null
          id?: string
          invoice_date?: string | null
          invoice_number?: string | null
          line_items_fp?: string
          net_amount?: number | null
          order_reference?: string | null
          processed_at?: string
          supplier_iban?: string | null
          supplier_name?: string | null
          total_quantity?: number | null
        }
        Relationships: []
      }
      orders: {
        Row: {
          artikel: string
          bestellnummer: string
          einzelpreis_netto: number
          lieferant: string
          menge: number
        }
        Insert: {
          artikel: string
          bestellnummer: string
          einzelpreis_netto: number
          lieferant: string
          menge: number
        }
        Update: {
          artikel?: string
          bestellnummer?: string
          einzelpreis_netto?: number
          lieferant?: string
          menge?: number
        }
        Relationships: []
      }
      overrides: {
        Row: {
          automatisch_war: string
          document_id: string
          entscheidung: string
          notiz: string
          user_id: string | null
          zeitpunkt: string
        }
        Insert: {
          automatisch_war?: string
          document_id: string
          entscheidung: string
          notiz?: string
          user_id?: string | null
          zeitpunkt?: string
        }
        Update: {
          automatisch_war?: string
          document_id?: string
          entscheidung?: string
          notiz?: string
          user_id?: string | null
          zeitpunkt?: string
        }
        Relationships: [
          {
            foreignKeyName: "overrides_document_id_fkey"
            columns: ["document_id"]
            isOneToOne: true
            referencedRelation: "documents"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends (DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never) = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends (PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never) = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
