"""StockPilot Pro — Industrial Warehouse & Cloud Inventory Logistics System."""

from datetime import datetime

import altair as alt
import streamlit as st

from core import (
    CATEGORIES,
    LocalInventoryStore,
    SupabaseInventoryStore,
    build_qr_label_sheet_html,
    compute_reorder_plan,
    generate_qr,
)

# ==============================================================================
# 1. PAGE & INDUSTRIAL LOGISTICS THEME
# ==============================================================================
st.set_page_config(
    page_title="StockPilot | Inventory & QR Operations",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .stApp {
        background: radial-gradient(960px 420px at 85% -10%, rgba(245,158,11,0.08), transparent), #111215;
        color: #f4f4f5;
    }
    section[data-testid="stSidebar"] {
        background-color: #16181d;
        border-right: 1px solid #27272a;
    }
    div[data-testid="metric-container"] {
        background-color: #181a20;
        border: 1px solid #27272a;
        border-top: 3px solid #f59e0b;
        padding: 14px 20px;
        border-radius: 8px;
        transition: border-color 0.15s ease;
    }
    div[data-testid="stMetricValue"] {
        color: #fafafa;
        font-weight: 700;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
    }
</style>
""",
    unsafe_allow_html=True,
)


# ==============================================================================
# 3. AUTHENTICATION & MODE SELECTION
# ==============================================================================
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = None

if not st.session_state.auth_mode:
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown("## 📦 StockPilot Logistics Console")
        st.caption("Cloud PostgreSQL (Supabase) & Local SQLite Inventory Operations")

        with st.container(border=True):
            password = st.text_input("Admin Password (Supabase Cloud)", type="password")
            c_login, c_demo = st.columns(2)
            with c_login:
                if st.button("Sign In (Cloud DB)", type="primary", use_container_width=True):
                    expected_pw = st.secrets.get("ADMIN_PASSWORD", "") if hasattr(st, "secrets") else ""
                    if expected_pw and password == expected_pw:
                        st.session_state.auth_mode = "supabase"
                        st.rerun()
                    else:
                        st.error("Invalid Admin Password or missing Supabase secrets.")
            with c_demo:
                if st.button("Launch Demo Workspace", use_container_width=True):
                    st.session_state.auth_mode = "local"
                    st.rerun()
    st.stop()


# Initialize active store
if st.session_state.auth_mode == "supabase":
    try:
        store = SupabaseInventoryStore(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    except Exception as exc:
        st.warning(f"Supabase unavailable ({exc}). Switching to local SQLite workspace.")
        store = LocalInventoryStore()
        st.session_state.auth_mode = "local"
else:
    store = LocalInventoryStore()


# ==============================================================================
# 4. SIDEBAR & NAVIGATION
# ==============================================================================
with st.sidebar:
    st.title("📦 StockPilot")
    mode_label = "Supabase Cloud" if st.session_state.auth_mode == "supabase" else "Local SQLite Demo"
    st.caption(f"Storage: {mode_label}")
    st.divider()
    menu = st.radio("Workspace", ["Dashboard", "Inventory", "Manage Items"])
    low_stock_threshold = st.slider("Low-Stock Alert Threshold", 1, 30, 10)
    st.divider()
    if st.button("Switch / Logout", use_container_width=True):
        st.session_state.auth_mode = None
        st.rerun()


# ==============================================================================
# 5. MAIN VIEWS
# ==============================================================================
df = store.fetch()

if menu == "Dashboard":
    st.title("Inventory Operations Overview")
    if df.empty:
        st.info("Inventory ledger is empty. Add items in Manage Items.")
    else:
        df["total_value"] = df["price"] * df["quantity"]
        low_stock_df = df[df["quantity"] < low_stock_threshold]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total SKUs", len(df))
        c2.metric("Low Stock Items", len(low_stock_df), delta=f"<{low_stock_threshold} units", delta_color="inverse")
        c3.metric("Total Asset Value", f"${df['total_value'].sum():,.2f}")
        c4.metric("Average Unit Price", f"${df['price'].mean():,.2f}")

        st.divider()
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.subheader("Stock Quantity by Product")
            bar_chart = (
                alt.Chart(df)
                .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
                .encode(
                    x=alt.X("name:N", sort="-y", title="Product"),
                    y=alt.Y("quantity:Q", title="Units"),
                    color=alt.Color(
                        "category:N",
                        scale=alt.Scale(range=["#f59e0b", "#38bdf8", "#10b981", "#a78bfa", "#94a3b8"]),
                    ),
                    tooltip=["name", "category", "price", "quantity"],
                )
                .properties(height=320, background="transparent")
            )
            st.altair_chart(bar_chart, use_container_width=True)

        with col_chart2:
            st.subheader("Valuation by Category")
            pie_chart = (
                alt.Chart(df)
                .mark_arc(innerRadius=58)
                .encode(
                    theta=alt.Theta(field="total_value", type="quantitative"),
                    color=alt.Color(
                        field="category",
                        type="nominal",
                        scale=alt.Scale(range=["#f59e0b", "#38bdf8", "#10b981", "#a78bfa", "#94a3b8"]),
                    ),
                    tooltip=["category", alt.Tooltip("total_value:Q", format="$,.2f")],
                )
                .properties(height=320, background="transparent")
            )
            st.altair_chart(pie_chart, use_container_width=True)

        reorder_df = compute_reorder_plan(df, threshold=low_stock_threshold, target_buffer=max(low_stock_threshold + 5, 15))
        if not reorder_df.empty:
            st.divider()
            r_head, r_cost = st.columns([3, 1])
            r_head.subheader("Reorder Planner & Quick Restock")
            r_cost.metric("Est. Restock Budget", f"${reorder_df['est_cost'].sum():,.2f}")
            st.dataframe(
                reorder_df,
                use_container_width=True,
                hide_index=True,
                column_config={"est_cost": st.column_config.NumberColumn("Est. Cost", format="$%.2f")},
            )
            if hasattr(store, "adjust_stock"):
                act_cols = st.columns([2, 1, 1])
                opts = {f"#{int(r['id'])} {r['name']} (qty {int(r['quantity'])})": int(r["id"]) for _, r in reorder_df.iterrows()}
                picked = act_cols[0].selectbox("Target Low-Stock SKU", list(opts.keys()), label_visibility="collapsed")
                target_id = opts[picked]
                if act_cols[1].button("Quick Restock (+10)", type="primary", use_container_width=True):
                    store.adjust_stock(target_id, 10, "Dashboard quick restock")
                    st.rerun()
                if act_cols[2].button("Dispatch (-1)", use_container_width=True):
                    store.adjust_stock(target_id, -1, "Dashboard dispatch")
                    st.rerun()

elif menu == "Inventory":
    st.title("Live Inventory Ledger")
    if df.empty:
        st.info("No items found.")
    else:
        col_search, col_cat, col_lvl, col_export = st.columns([2, 1, 1, 1])
        search = col_search.text_input("Search SKU or Product Name", placeholder="e.g. Cisco, Laptop...")
        selected_cat = col_cat.selectbox("Category Filter", ["All"] + CATEGORIES)
        stock_lvl = col_lvl.selectbox("Stock Level", ["All Stock", "Low Stock Only"])

        filtered = df.copy()
        if search:
            filtered = filtered[filtered["name"].str.contains(search, case=False, na=False)]
        if selected_cat != "All":
            filtered = filtered[filtered["category"] == selected_cat]
        if stock_lvl == "Low Stock Only":
            filtered = filtered[filtered["quantity"] < low_stock_threshold]

        col_export.markdown("<br>", unsafe_allow_html=True)
        col_export.download_button(
            "Export CSV Report",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name=f"stockpilot_inventory_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

        max_qty = int(filtered["quantity"].max()) if not filtered.empty and filtered["quantity"].max() > 0 else 100
        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True,
            column_config={
                "price": st.column_config.NumberColumn("Unit Price", format="$%.2f"),
                "quantity": st.column_config.ProgressColumn("Stock Level", format="%d", min_value=0, max_value=max_qty),
            },
        )

        if hasattr(store, "fetch_movements"):
            mv = store.fetch_movements()
            if not mv.empty:
                st.divider()
                st.subheader("Recent Stock Movement Ledger")
                st.dataframe(mv, use_container_width=True, hide_index=True)

elif menu == "Manage Items":
    st.title("SKU Operations & QR Tagging")
    tab1, tab2, tab3, tab4 = st.tabs(["Add Item", "Edit & Generate QR", "Batch CSV & Print Labels", "Delete Item"])

    with tab1:
        with st.form("add_sku_form"):
            c1, c2 = st.columns(2)
            n_name = c1.text_input("Product Name")
            n_cat = c2.selectbox("Category", CATEGORIES)
            c3, c4 = st.columns(2)
            n_price = c3.number_input("Unit Price ($)", min_value=0.01, value=25.00, step=0.50)
            n_qty = c4.number_input("Initial Quantity", min_value=0, value=10, step=1)
            if st.form_submit_button("Save Product", type="primary"):
                if not n_name.strip():
                    st.error("Product name is required.")
                else:
                    ok, err = store.add(n_name.strip(), n_cat, float(n_price), int(n_qty))
                    if ok:
                        st.success("Product saved to inventory.")
                        st.rerun()
                    else:
                        st.error(f"Failed to save product: {err}")

    with tab2:
        if df.empty:
            st.info("No products available to edit.")
        else:
            options = {f"#{int(r['id'])} — {r['name']}": int(r["id"]) for _, r in df.iterrows()}
            chosen_label = st.selectbox("Select Product", list(options.keys()))
            edit_id = options[chosen_label]
            row = df[df["id"] == edit_id].iloc[0]

            current_cat_idx = CATEGORIES.index(row["category"]) if row["category"] in CATEGORIES else 0
            with st.form("edit_sku_form"):
                c1, c2 = st.columns(2)
                e_name = c1.text_input("Product Name", value=str(row["name"]))
                e_cat = c2.selectbox("Category", CATEGORIES, index=current_cat_idx)
                c3, c4 = st.columns(2)
                e_price = c3.number_input("Unit Price ($)", min_value=0.01, value=float(row["price"]))
                e_qty = c4.number_input("Quantity", min_value=0, value=int(row["quantity"]))
                if st.form_submit_button("Update Product", type="primary"):
                    ok, err = store.update(edit_id, e_name.strip(), e_cat, float(e_price), int(e_qty))
                    if ok:
                        st.success("Product updated.")
                        st.rerun()
                    else:
                        st.error(f"Update failed: {err}")

            st.divider()
            qr_payload = f"STOCKPILOT|ID:{edit_id}|NAME:{row['name']}|CAT:{row['category']}"
            qr_bytes = generate_qr(qr_payload)
            c_qr, c_meta = st.columns([1, 3])
            c_qr.image(qr_bytes, width=160, caption=f"SKU #{edit_id} Tag")
            c_meta.download_button(
                "Download QR Tag (PNG)",
                data=qr_bytes,
                file_name=f"sku_{edit_id}_qr.png",
                mime="image/png",
            )

    with tab3:
        st.subheader("Bulk CSV Import & Printable Multi-SKU QR Label Grid")
        uploaded_csv = st.file_uploader("Upload CSV (columns: name,category,price,quantity)", type=["csv"])
        if uploaded_csv is not None and hasattr(store, "import_csv"):
            if st.button("Import CSV Rows"):
                count_ok, errs = store.import_csv(uploaded_csv.getvalue().decode("utf-8", errors="replace"))
                st.success(f"Imported {count_ok} SKU rows.")
                if errs:
                    st.warning("; ".join(errs))
                st.rerun()

        if not df.empty:
            sheet_html = build_qr_label_sheet_html(df)
            st.download_button(
                "Download Printable Multi-SKU QR Label Grid (HTML)",
                data=sheet_html.encode("utf-8"),
                file_name="stockpilot_qr_sheet.html",
                mime="text/html",
            )

    with tab4:
        if df.empty:
            st.info("No products available to delete.")
        else:
            del_options = {f"#{int(r['id'])} — {r['name']}": int(r["id"]) for _, r in df.iterrows()}
            del_label = st.selectbox("Select Product to Remove", list(del_options.keys()), key="del_select")
            if st.button("Delete Selected SKU", type="primary"):
                ok, err = store.delete(del_options[del_label])
                if ok:
                    st.success("Product deleted.")
                    st.rerun()
                else:
                    st.error(f"Delete failed: {err}")
