from . import models

# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def post_init_add_indexes(cr, registry):
    """Post-init hook untuk menambahkan index di stock_valuation_layer"""
    # Index untuk filter product_id + create_date
    cr.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE c.relname = 'idx_svl_product_date'
            ) THEN
                CREATE INDEX idx_svl_product_date
                ON stock_valuation_layer (product_id, create_date);
            END IF;
        END $$;
    """)

    # Index untuk join ke stock_move
    cr.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE c.relname = 'idx_svl_move'
            ) THEN
                CREATE INDEX idx_svl_move
                ON stock_valuation_layer (stock_move_id);
            END IF;
        END $$;
    """)
