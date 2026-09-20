import streamlit as st
import pandas as pd
import datetime
import os

# =========================================================
# تنظیمات صفحه
# =========================================================

st.set_page_config(
    page_title="حسابداری شخصی",
    page_icon="💰",
    layout="wide"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

html, body, [class*="css"] {
    direction: rtl;
}

body, div, input, select, textarea, button, p,
h1, h2, h3, h4, h5, h6 {
    font-family: Tahoma, Vazir, sans-serif;
}

.stMetric {
    background-color: #f0f2f6;
    padding: 15px;
    border-radius: 10px;
}

div[data-testid="stMetricValue"] {
    direction: rtl;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# فایل دیتابیس
# =========================================================

DB_FILE = "transactions.csv"

COLUMNS = [
    "شناسه",
    "تاریخ",
    "نوع",
    "دسته‌بندی",
    "مبلغ (تومان)",
    "توضیحات"
]


# =========================================================
# ایجاد دیتابیس در صورت نبودن
# =========================================================

if not os.path.exists(DB_FILE):

    df_init = pd.DataFrame(columns=COLUMNS)

    df_init.to_csv(
        DB_FILE,
        index=False,
        encoding="utf-8-sig"
    )


# =========================================================
# خواندن اطلاعات
# =========================================================

def load_data():

    try:

        df = pd.read_csv(
            DB_FILE,
            encoding="utf-8-sig"
        )

    except Exception:

        df = pd.DataFrame(columns=COLUMNS)

    # اگر ستون شناسه وجود نداشت
    if "شناسه" not in df.columns:

        df.insert(
            0,
            "شناسه",
            range(1, len(df) + 1)
        )

    # اطمینان از وجود تمام ستون‌ها
    for col in COLUMNS:

        if col not in df.columns:
            df[col] = ""

    # ترتیب ستون‌ها
    df = df[COLUMNS]

    # تبدیل مبلغ به عدد
    df["مبلغ (تومان)"] = pd.to_numeric(
        df["مبلغ (تومان)"],
        errors="coerce"
    ).fillna(0)

    # تبدیل شناسه به عدد
    df["شناسه"] = pd.to_numeric(
        df["شناسه"],
        errors="coerce"
    )

    # ساخت شناسه در صورت خراب بودن
    if df["شناسه"].isna().any():

        max_id = (
            int(df["شناسه"].dropna().max())
            if not df["شناسه"].dropna().empty
            else 0
        )

        missing = df["شناسه"].isna()

        df.loc[missing, "شناسه"] = range(
            max_id + 1,
            max_id + 1 + missing.sum()
        )

    df["شناسه"] = df["شناسه"].astype(int)

    return df


# =========================================================
# ذخیره اطلاعات
# =========================================================

def save_data(data):

    data.to_csv(
        DB_FILE,
        index=False,
        encoding="utf-8-sig"
    )


# =========================================================
# دسته‌بندی‌ها
# =========================================================

expense_categories = [
    "خرید / سوپرمارکت",
    "بنزین و خودرو",
    "شارژ و اینترنت",
    "اجاره و قبوض",
    "تفریح و سرگرمی",
    "پوشاک",
    "غذا و رستوران",
    "سلامت و درمان",
    "آموزش",
    "سفر",
    "سایر"
]

income_categories = [
    "حقوق",
    "پاداش",
    "فروش",
    "سرمایه‌گذاری",
    "سایر"
]


# =========================================================
# عنوان
# =========================================================

st.title("💰 سیستم حسابداری شخصی")

st.caption(
    "مدیریت درآمد، هزینه، موجودی و گزارش‌های مالی شخصی"
)

st.write("---")


# =========================================================
# بارگذاری دیتابیس
# =========================================================

df = load_data()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("➕ ثبت تراکنش جدید")

date = st.sidebar.date_input(
    "📅 تاریخ",
    datetime.date.today()
)

trans_type = st.sidebar.selectbox(
    "🔄 نوع تراکنش",
    ["هزینه", "درآمد"]
)


# دسته‌بندی بر اساس نوع تراکنش
if trans_type == "هزینه":

    category_list = expense_categories

else:

    category_list = income_categories


category = st.sidebar.selectbox(
    "📂 دسته‌بندی",
    category_list
)


amount = st.sidebar.number_input(
    "💵 مبلغ (تومان)",
    min_value=0,
    step=10000,
    format="%d"
)


description = st.sidebar.text_input(
    "📝 توضیحات"
)


# =========================================================
# ثبت تراکنش
# =========================================================

if st.sidebar.button(
    "✅ ثبت تراکنش",
    use_container_width=True
):

    if amount > 0:

        if df.empty:

            new_id = 1

        else:

            new_id = int(df["شناسه"].max()) + 1

        new_row = pd.DataFrame([{

            "شناسه": new_id,

            "تاریخ": str(date),

            "نوع": trans_type,

            "دسته‌بندی": category,

            "مبلغ (تومان)": amount,

            "توضیحات": description

        }])

        df = pd.concat(
            [df, new_row],
            ignore_index=True
        )

        save_data(df)

        st.sidebar.success(
            "تراکنش با موفقیت ثبت شد."
        )

        st.rerun()

    else:

        st.sidebar.error(
            "لطفاً مبلغ را بیشتر از صفر وارد کنید."
        )


# =========================================================
# محاسبات کلی
# =========================================================

total_income = df[
    df["نوع"] == "درآمد"
]["مبلغ (تومان)"].sum()

total_expense = df[
    df["نوع"] == "هزینه"
]["مبلغ (تومان)"].sum()

balance = total_income - total_expense


# =========================================================
# کارت‌های اصلی
# =========================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💵 کل درآمد",
    f"{total_income:,.0f} تومان"
)

col2.metric(
    "💸 کل هزینه",
    f"{total_expense:,.0f} تومان"
)

col3.metric(
    "💰 مانده",
    f"{balance:,.0f} تومان"
)

col4.metric(
    "📋 تعداد تراکنش",
    f"{len(df):,}"
)


st.write("---")


# =========================================================
# اگر تراکنشی وجود داشته باشد
# =========================================================

if not df.empty:

    # =====================================================
    # تب‌ها
    # =====================================================

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 داشبورد",
        "📋 تراکنش‌ها",
        "✏️ ویرایش / حذف",
        "📥 خروجی"
    ])


    # =====================================================
    # TAB 1 - داشبورد
    # =====================================================

    with tab1:

        st.subheader("📊 تحلیل مالی")

        # -----------------------------------------------
        # درآمد و هزینه ماه جاری
        # -----------------------------------------------

        current_month = datetime.date.today().strftime(
            "%Y-%m"
        )

        df["ماه"] = df["تاریخ"].astype(str).str[:7]

        month_df = df[
            df["ماه"] == current_month
        ]

        month_income = month_df[
            month_df["نوع"] == "درآمد"
        ]["مبلغ (تومان)"].sum()

        month_expense = month_df[
            month_df["نوع"] == "هزینه"
        ]["مبلغ (تومان)"].sum()

        month_balance = (
            month_income - month_expense
        )


        m1, m2, m3 = st.columns(3)

        m1.metric(
            "درآمد این ماه",
            f"{month_income:,.0f} تومان"
        )

        m2.metric(
            "هزینه این ماه",
            f"{month_expense:,.0f} تومان"
        )

        m3.metric(
            "مانده این ماه",
            f"{month_balance:,.0f} تومان"
        )


        st.write("---")


        # =================================================
        # نمودار هزینه‌ها
        # =================================================

        expense_df = df[
            df["نوع"] == "هزینه"
        ]

        if not expense_df.empty:

            st.subheader(
                "💸 هزینه‌ها بر اساس دسته‌بندی"
            )

            cat_summary = (
                expense_df
                .groupby("دسته‌بندی")[
                    "مبلغ (تومان)"
                ]
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            st.bar_chart(cat_summary)


        # =================================================
        # درآمدها
        # =================================================

        income_df = df[
            df["نوع"] == "درآمد"
        ]

        if not income_df.empty:

            st.subheader(
                "💵 درآمدها بر اساس دسته‌بندی"
            )

            income_summary = (
                income_df
                .groupby("دسته‌بندی")[
                    "مبلغ (تومان)"
                ]
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            st.bar_chart(income_summary)


        # =================================================
        # خلاصه ماه‌ها
        # =================================================

        st.subheader(
            "📅 گزارش ماهانه"
        )

        monthly_income = (
            df[df["نوع"] == "درآمد"]
            .groupby("ماه")[
                "مبلغ (تومان)"
            ]
            .sum()
        )

        monthly_expense = (
            df[df["نوع"] == "هزینه"]
            .groupby("ماه")[
                "مبلغ (تومان)"
            ]
            .sum()
        )

        monthly_report = pd.DataFrame({

            "درآمد": monthly_income,

            "هزینه": monthly_expense

        }).fillna(0)

        monthly_report["مانده"] = (
            monthly_report["درآمد"]
            - monthly_report["هزینه"]
        )

        st.dataframe(
            monthly_report.sort_index(
                ascending=False
            ),
            use_container_width=True
        )


    # =====================================================
    # TAB 2 - تراکنش‌ها
    # =====================================================

    with tab2:

        st.subheader(
            "📋 لیست تراکنش‌ها"
        )


        # -----------------------------------------------
        # جستجو
        # -----------------------------------------------

        search = st.text_input(
            "🔎 جستجو",
            placeholder="دسته‌بندی، توضیحات یا مبلغ..."
        )


        # -----------------------------------------------
        # فیلتر نوع
        # -----------------------------------------------

        filter_type = st.selectbox(
            "نوع تراکنش",
            [
                "همه",
                "درآمد",
                "هزینه"
            ]
        )


        filtered_df = df.copy()


        if filter_type != "همه":

            filtered_df = filtered_df[
                filtered_df["نوع"] == filter_type
            ]


        # -----------------------------------------------
        # جستجو
        # -----------------------------------------------

        if search:

            search = search.lower()

            filtered_df = filtered_df[
                filtered_df.astype(str)
                .apply(
                    lambda row:
                    row.str.lower()
                    .str.contains(
                        search,
                        na=False
                    ).any(),
                    axis=1
                )
            ]


        # -----------------------------------------------
        # نمایش
        # -----------------------------------------------

        display_df = filtered_df.drop(
            columns=["ماه"],
            errors="ignore"
        )

        st.dataframe(
            display_df.sort_values(
                "شناسه",
                ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )


    # =====================================================
    # TAB 3 - ویرایش / حذف
    # =====================================================

    with tab3:

        st.subheader(
            "✏️ مدیریت تراکنش‌ها"
        )


        transaction_ids = df[
            "شناسه"
        ].tolist()


        selected_id = st.selectbox(
            "تراکنش موردنظر را انتخاب کنید",
            transaction_ids
        )


        selected = df[
            df["شناسه"] == selected_id
        ].iloc[0]


        st.write(
            f"**تراکنش انتخاب‌شده:** "
            f"{selected['نوع']} - "
            f"{selected['مبلغ (تومان)']:,.0f} تومان"
        )


        # -----------------------------------------------
        # فرم ویرایش
        # -----------------------------------------------

        edit_date = st.date_input(
            "تاریخ جدید",
            datetime.datetime.strptime(
                str(selected["تاریخ"]),
                "%Y-%m-%d"
            ).date()
        )


        edit_type = st.selectbox(
            "نوع جدید",
            ["هزینه", "درآمد"],
            index=(
                0
                if selected["نوع"] == "هزینه"
                else 1
            )
        )


        if edit_type == "هزینه":

            edit_categories = expense_categories

        else:

            edit_categories = income_categories


        current_category = selected[
            "دسته‌بندی"
        ]

        if current_category not in edit_categories:

            edit_categories = (
                edit_categories
                + [current_category]
            )


        edit_category = st.selectbox(
            "دسته‌بندی جدید",
            edit_categories,
            index=edit_categories.index(
                current_category
            )
        )


        edit_amount = st.number_input(
            "مبلغ جدید",
            min_value=0,
            value=int(
                selected["مبلغ (تومان)"]
            ),
            step=10000
        )


        edit_description = st.text_input(
            "توضیحات جدید",
            value=str(
                selected["توضیحات"]
            )
        )


        col_edit, col_delete = st.columns(2)


        # -----------------------------------------------
        # دکمه ویرایش
        # -----------------------------------------------

        with col_edit:

            if st.button(
                "💾 ذخیره تغییرات",
                use_container_width=True
            ):

                if edit_amount > 0:

                    index = df[
                        df["شناسه"] == selected_id
                    ].index[0]


                    df.loc[
                        index,
                        "تاریخ"
                    ] = str(edit_date)


                    df.loc[
                        index,
                        "نوع"
                    ] = edit_type


                    df.loc[
                        index,
                        "دسته‌بندی"
                    ] = edit_category


                    df.loc[
                        index,
                        "مبلغ (تومان)"
                    ] = edit_amount


                    df.loc[
                        index,
                        "توضیحات"
                    ] = edit_description


                    save_data(df)

                    st.success(
                        "تراکنش با موفقیت ویرایش شد."
                    )

                    st.rerun()

                else:

                    st.error(
                        "مبلغ باید بیشتر از صفر باشد."
                    )


        # -----------------------------------------------
        # حذف
        # -----------------------------------------------

        with col_delete:

            if st.button(
                "🗑️ حذف تراکنش",
                use_container_width=True
            ):

                df = df[
                    df["شناسه"] != selected_id
                ]

                save_data(df)

                st.success(
                    "تراکنش حذف شد."
                )

                st.rerun()


    # =====================================================
    # TAB 4 - خروجی
    # =====================================================

    with tab4:

        st.subheader(
            "📥 دریافت اطلاعات"
        )


        export_df = df.drop(
            columns=["ماه"],
            errors="ignore"
        )


        csv_data = export_df.to_csv(
            index=False,
            encoding="utf-8-sig"
        )


        st.download_button(
            label="📥 دانلود فایل CSV",
            data=csv_data,
            file_name="حسابداری_شخصی.csv",
            mime="text/csv",
            use_container_width=True
        )


        st.info(
            "این فایل را می‌توانید به عنوان نسخه "
            "پشتیبان تراکنش‌های خود نگهداری کنید."
        )


# =========================================================
# حالت بدون تراکنش
# =========================================================

else:

    st.info(
        "📭 هنوز هیچ تراکنشی ثبت نشده است."
        " از منوی سمت راست اولین تراکنش خود را ثبت کنید."
    )


# =========================================================
# فوتر
# =========================================================

st.write("---")

st.caption(
    "💰 سیستم حسابداری شخصی | نسخه مدیریت تراکنش‌ها"
)
