import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

# -----------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------
st.set_page_config(
    page_title="CHRIST Campus Venue Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Venue lookup reference with CHRIST Central Campus coordinates
VENUE_INFO = {
    "Main Auditorium": {"block": "Audi Block", "cap": 800, "lat": 12.93572, "lon": 77.60590},
    "KE Auditorium": {"block": "Block IV", "cap": 500, "lat": 12.93180, "lon": 77.60582},
    "Assembly Hall": {"block": "Block I", "cap": 300, "lat": 12.93405, "lon": 77.60685},
    "Skyview": {"block": "Central Block", "cap": 250, "lat": 12.93452, "lon": 77.60590},
    "Panel Room 1": {"block": "Block II", "cap": 100, "lat": 12.93285, "lon": 77.60642},
    "Panel Room 2": {"block": "Block II", "cap": 100, "lat": 12.93295, "lon": 77.60648}
}

# -----------------------------------------------------------------------
# Initialize Dataset in Session State
# -----------------------------------------------------------------------
if "events_df" not in st.session_state:
    st.session_state.events_df = pd.read_csv("christ_campus_events.csv")

df = st.session_state.events_df.copy()

# Pandas & NumPy feature preparation
df["Date_dt"] = pd.to_datetime(df["Date"])
df["Month"] = df["Date_dt"].dt.month_name()
df["Duration_Hrs"] = df["End_Hour"] - df["Start_Hour"]
df["Utilization_Pct"] = np.round((df["Expected_Footfall"] / df["Venue_Capacity"]) * 100, 1)

# -----------------------------------------------------------------------
# Sidebar Navigation & Multi-Control Filters
# -----------------------------------------------------------------------
all_venues = sorted(df["Venue"].unique().tolist())
all_depts = sorted(df["Department"].unique().tolist())
all_statuses = sorted(df["Booking_Status"].unique().tolist())

# Initialize filter defaults in session state
if "filter_period" not in st.session_state:
    st.session_state.filter_period = "All"
if "filter_venues" not in st.session_state:
    st.session_state.filter_venues = all_venues
if "filter_depts" not in st.session_state:
    st.session_state.filter_depts = all_depts
if "filter_statuses" not in st.session_state:
    st.session_state.filter_statuses = all_statuses
if "filter_util" not in st.session_state:
    st.session_state.filter_util = (0, 100)

def reset_filters():
    st.session_state.filter_period = "All"
    st.session_state.filter_venues = all_venues
    st.session_state.filter_depts = all_depts
    st.session_state.filter_statuses = all_statuses
    st.session_state.filter_util = (0, 100)

with st.sidebar:
    st.markdown("### CHRIST Venue Console")
    st.caption("Central Campus Auditorium, Seminar Hall & Event Clash Analytics")
    st.divider()

    period_options = ["All", "Aug", "Sep", "Oct", "Nov"]
    period_choice = st.segmented_control(
        "Month Filter",
        options=period_options,
        key="filter_period"
    )

    selected_venues = st.multiselect("Campus Venues", options=all_venues, key="filter_venues")
    selected_depts = st.multiselect("Organizing Departments", options=all_depts, key="filter_depts")
    selected_statuses = st.multiselect("Booking Status", options=all_statuses, key="filter_statuses")
    util_range = st.slider("Hall Utilization Range (%)", 0, 100, key="filter_util")

    st.divider()
    st.button("Reset Filters", on_click=reset_filters, use_container_width=True)
    
# -----------------------------------------------------------------------
# Header & 2 Top-Level Tabs (Analytics & Registration)
# -----------------------------------------------------------------------
st.title("CHRIST Campus Venue Utilization & Event Analytics")
st.caption("Auditorium Occupancy, Scheduling Clash Diagnostics & Departmental Demand Telemetry")

tab_analytics, tab_registration = st.tabs(["Analytics", "Registration"])

# =======================================================================
# TOP TAB 1: ANALYTICS (Contains KPIs + 5 Sub-Tabs including Map)
# =======================================================================
with tab_analytics:
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    total_events = len(filtered_df)
    total_footfall = int(np.sum(filtered_df["Expected_Footfall"])) if total_events > 0 else 0
    avg_util = float(np.mean(filtered_df["Utilization_Pct"])) if total_events > 0 else 0.0
    overall_avg_util = float(np.mean(df["Utilization_Pct"]))
    clash_count = int(np.sum(filtered_df["Booking_Status"] == "Clash Flagged"))
    total_power = float(np.sum(filtered_df["Est_Power_kWh"])) if total_events > 0 else 0.0

    kpi1.metric(
        label="Total Events",
        value=f"{total_events:,}",
        delta=f"{total_events - len(df)} vs All" if total_events != len(df) else "Full Dataset",
        border=True
    )
    kpi2.metric(
        label="Expected Footfall",
        value=f"{total_footfall:,}",
        delta=f"{int(np.mean(filtered_df['Expected_Footfall'])) if total_events > 0 else 0} avg/event",
        delta_color="off",
        border=True
    )
    kpi3.metric(
        label="Avg Hall Utilization",
        value=f"{avg_util:.1f}%",
        delta=f"{avg_util - overall_avg_util:+.1f}% vs Sem Avg",
        border=True
    )
    kpi4.metric(
        label="Clashes Flagged",
        value=f"{clash_count}",
        delta="Schedule Conflicts",
        delta_color="off",
        border=True
    )
    kpi5.metric(
        label="Est. Energy Load",
        value=f"{total_power:,.1f}",
        delta="Total kWh",
        delta_color="off",
        border=True
    )

    st.write("")

    # 5 Sub-Tabs Inside Analytics
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Venue & Time Trends",
        "Department & Event Insights",
        "Clash & Capacity Diagnostics",
        "Campus Venue Map",
        "Data Explorer & Stats"
    ])

    # -------------------------------------------------------------------
    # SUB-TAB 1: VENUE & TIME TRENDS
    # -------------------------------------------------------------------
    with tab1:
        if filtered_df.empty:
            st.warning("No records match the current filter selection.")
        else:
            col1, col2 = st.columns([3, 2])

            with col1:
                with st.container(border=True):
                    st.subheader("Cumulative Footfall by Campus Venue")
                    st.caption("Total student attendance demand across Central Campus auditoriums and halls.")
                    venue_group = filtered_df.groupby("Venue")["Expected_Footfall"].sum().sort_values(ascending=True)
                    fig1, ax1 = plt.subplots(figsize=(6.5, 3.8))
                    bars = ax1.barh(venue_group.index, venue_group.values, color="#1d4ed8", edgecolor="#1e3a8a")
                    ax1.bar_label(bars, padding=4, fmt="%d", fontsize=8)
                    ax1.set_xlabel("Expected Footfall")
                    ax1.set_xlim(0, venue_group.max() * 1.15)
                    ax1.spines["top"].set_visible(False)
                    ax1.spines["right"].set_visible(False)
                    ax1.grid(axis="x", linestyle="--", alpha=0.4)
                    st.pyplot(fig1)

            with col2:
                with st.container(border=True):
                    st.subheader("Booking Status Breakdown")
                    st.caption("Proportion of completed, scheduled, flagged, and cancelled bookings.")
                    status_counts = filtered_df["Booking_Status"].value_counts()
                    status_colors = {
                        "Completed": "#16a34a",
                        "Scheduled": "#2563eb",
                        "Clash Flagged": "#dc2626",
                        "Cancelled": "#d97706"
                    }
                    colors = [status_colors.get(s, "#64748b") for s in status_counts.index]
                    fig3, ax3 = plt.subplots(figsize=(5.5, 3.8))
                    wedges, _, autotexts = ax3.pie(
                        status_counts.values,
                        autopct="%1.1f%%",
                        startangle=140,
                        pctdistance=0.77,
                        colors=colors,
                        wedgeprops=dict(width=0.45, edgecolor="white", linewidth=1.5),
                        textprops=dict(color="white", fontweight="bold", fontsize=8.5)
                    )
                    ax3.legend(
                        wedges,
                        status_counts.index,
                        loc="lower center",
                        bbox_to_anchor=(0.5, -0.14),
                        ncol=2,
                        frameon=False,
                        fontsize=9
                    )
                    ax3.axis("equal")
                    st.pyplot(fig3)

            st.write("")
            col3, col4 = st.columns(2)

            with col3:
                with st.container(border=True):
                    st.subheader("Monthly Campus Event Demand Trend")
                    st.caption("Progression of total expected footfall across semester months.")
                    month_order = ["August", "September", "October", "November"]
                    monthly_trend = (
                        filtered_df.groupby("Month", observed=False)["Expected_Footfall"]
                        .sum()
                        .reindex(month_order)
                        .dropna()
                    )
                    fig2, ax2 = plt.subplots(figsize=(6, 3.6))
                    ax2.plot(monthly_trend.index, monthly_trend.values, marker="o", linewidth=2.2, color="#0d9488")
                    ax2.fill_between(monthly_trend.index, monthly_trend.values, color="#0d9488", alpha=0.12)
                    ax2.set_xlabel("Semester Month")
                    ax2.set_ylabel("Total Expected Footfall")
                    ax2.spines["top"].set_visible(False)
                    ax2.spines["right"].set_visible(False)
                    ax2.grid(True, linestyle="--", alpha=0.4)
                    st.pyplot(fig2)

            with col4:
                with st.container(border=True):
                    st.subheader("Peak Event Start Hours")
                    st.caption("Distribution of event start times across the 24-hour academic schedule.")
                    hour_counts = filtered_df["Start_Hour"].value_counts().sort_index()
                    fig4, ax4 = plt.subplots(figsize=(6, 3.6))
                    ax4.bar(hour_counts.index.astype(str) + ":00", hour_counts.values, color="#2563eb", edgecolor="#1e3a8a")
                    ax4.set_xlabel("Start Hour")
                    ax4.set_ylabel("Number of Events")
                    ax4.spines["top"].set_visible(False)
                    ax4.spines["right"].set_visible(False)
                    ax4.grid(axis="y", linestyle="--", alpha=0.4)
                    st.pyplot(fig4)

    # -------------------------------------------------------------------
    # SUB-TAB 2: DEPARTMENT & EVENT INSIGHTS
    # -------------------------------------------------------------------
    with tab2:
        if filtered_df.empty:
            st.warning("No records match the current filter selection.")
        else:
            c1, c2 = st.columns(2)

            with c1:
                with st.container(border=True):
                    st.subheader("Events Organized by Department")
                    st.caption("Total venue reservations initiated per academic department.")
                    dept_counts = filtered_df["Department"].value_counts()
                    fig5, ax5 = plt.subplots(figsize=(6, 4))
                    ax5.bar(dept_counts.index, dept_counts.values, color="#4f46e5", edgecolor="#312e81")
                    ax5.set_ylabel("Event Count")
                    plt.xticks(rotation=35, ha="right")
                    ax5.spines["top"].set_visible(False)
                    ax5.spines["right"].set_visible(False)
                    ax5.grid(axis="y", linestyle="--", alpha=0.4)
                    st.pyplot(fig5)

            with c2:
                with st.container(border=True):
                    st.subheader("Average Utilization (%) by Event Type")
                    st.caption("Mean seating capacity utilization across different event formats.")
                    type_util = filtered_df.groupby("Event_Type")["Utilization_Pct"].mean().sort_values(ascending=False)
                    fig6, ax6 = plt.subplots(figsize=(6, 4))
                    ax6.bar(type_util.index, type_util.values, color="#0284c7", edgecolor="#0c4a6e")
                    ax6.set_ylabel("Avg Utilization (%)")
                    plt.xticks(rotation=35, ha="right")
                    ax6.spines["top"].set_visible(False)
                    ax6.spines["right"].set_visible(False)
                    ax6.grid(axis="y", linestyle="--", alpha=0.4)
                    st.pyplot(fig6)

            st.write("")
            with st.container(border=True):
                st.subheader("Department vs Venue Footfall Matrix (Pivot Table)")
                st.caption("Color-graded cross-tabulation of cumulative expected student footfall across venues.")
                pivot_matrix = pd.pivot_table(
                    filtered_df,
                    values="Expected_Footfall",
                    index="Department",
                    columns="Venue",
                    aggfunc="sum",
                    fill_value=0
                )
                styled_pivot = pivot_matrix.style.background_gradient(cmap="Blues")
                st.dataframe(styled_pivot, use_container_width=True)

    # -------------------------------------------------------------------
    # SUB-TAB 3: CLASH & CAPACITY DIAGNOSTICS
    # -------------------------------------------------------------------
    with tab3:
        if filtered_df.empty:
            st.warning("No records match the current filter selection.")
        else:
            sc1, sc2 = st.columns(2)

            with sc1:
                with st.container(border=True):
                    st.subheader("Expected vs Actual Footfall (Completed Events)")
                    st.caption("Forecast accuracy comparing projected turnout against recorded attendance.")
                    completed_df = filtered_df[filtered_df["Booking_Status"] == "Completed"]
                    fig7, ax7 = plt.subplots(figsize=(6, 3.8))
                    ax7.scatter(
                        completed_df["Expected_Footfall"],
                        completed_df["Actual_Footfall"],
                        alpha=0.75,
                        color="#0d9488",
                        edgecolors="#115e59"
                    )
                    if not completed_df.empty:
                        max_val = max(completed_df["Expected_Footfall"].max(), completed_df["Actual_Footfall"].max())
                        ax7.plot([0, max_val], [0, max_val], color="#dc2626", linestyle="--", label="100% Forecast Match")
                        ax7.legend()
                    ax7.set_xlabel("Expected Footfall")
                    ax7.set_ylabel("Actual Footfall")
                    ax7.spines["top"].set_visible(False)
                    ax7.spines["right"].set_visible(False)
                    ax7.grid(True, linestyle="--", alpha=0.4)
                    st.pyplot(fig7)

            with sc2:
                with st.container(border=True):
                    st.subheader("Distribution of Venue Utilization (%)")
                    st.caption("Frequency distribution of seating occupancy rates across all filtered bookings.")
                    fig8, ax8 = plt.subplots(figsize=(6, 3.8))
                    ax8.hist(filtered_df["Utilization_Pct"], bins=12, color="#2563eb", edgecolor="white", alpha=0.9)
                    ax8.axvline(np.mean(filtered_df["Utilization_Pct"]), color="#dc2626", linestyle="--", linewidth=1.8, label="Mean Utilization")
                    ax8.set_xlabel("Utilization (%)")
                    ax8.set_ylabel("Frequency")
                    ax8.legend()
                    ax8.spines["top"].set_visible(False)
                    ax8.spines["right"].set_visible(False)
                    ax8.grid(axis="y", linestyle="--", alpha=0.4)
                    st.pyplot(fig8)

            st.write("")
            with st.container(border=True):
                st.subheader("Flagged Scheduling Clashes & High-Load Alerts")
                st.caption("Events flagged due to overlapping venue time slots requiring coordinator intervention.")
                clash_df = filtered_df[filtered_df["Booking_Status"] == "Clash Flagged"]
                if clash_df.empty:
                    st.success("No scheduling clashes found in the filtered selection.")
                else:
                    st.dataframe(
                        clash_df[["Event_ID", "Event_Name", "Department", "Venue", "Date", "Start_Hour", "End_Hour", "Expected_Footfall", "Utilization_Pct"]],
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Utilization_Pct": st.column_config.ProgressColumn(
                                "Capacity Load", min_value=0, max_value=100, format="%.1f%%"
                            )
                        }
                    )

    # -------------------------------------------------------------------
    # SUB-TAB 4: CAMPUS VENUE MAP
    # -------------------------------------------------------------------
    with tab4:
        with st.container(border=True):
            st.subheader("CHRIST University Bengaluru Campus — Geospatial Venue Utilization Map")
            st.caption("Circle diameter represents cumulative event footfall; color intensity indicates average hall utilization rate (%).")
            if not filtered_df.empty:
                venue_spatial = (
                    filtered_df.groupby(["Venue", "Block", "Venue_Capacity"], as_index=False)
                    .agg(
                        Total_Events=("Event_ID", "count"),
                        Total_Footfall=("Expected_Footfall", "sum"),
                        Avg_Utilization=("Utilization_Pct", lambda s: round(s.mean(), 1)),
                        Clashes=("Booking_Status", lambda s: int((s == "Clash Flagged").sum()))
                    )
                )
                venue_spatial["latitude"] = venue_spatial["Venue"].map(lambda v: VENUE_INFO[v]["lat"])
                venue_spatial["longitude"] = venue_spatial["Venue"].map(lambda v: VENUE_INFO[v]["lon"])

                fig_map = px.scatter_map(
                    venue_spatial,
                    lat="latitude",
                    lon="longitude",
                    size="Total_Footfall",
                    color="Avg_Utilization",
                    color_continuous_scale="Blues",
                    size_max=34,
                    hover_name="Venue",
                    hover_data={
                        "Block": True,
                        "Venue_Capacity": True,
                        "Total_Events": True,
                        "Total_Footfall": True,
                        "Avg_Utilization": True,
                        "Clashes": True,
                        "latitude": False,
                        "longitude": False
                    },
                    labels={
                        "Venue_Capacity": "Max Capacity",
                        "Total_Events": "Scheduled Events",
                        "Total_Footfall": "Cumulative Footfall",
                        "Avg_Utilization": "Avg Utilization (%)"
                    },
                    center={"lat": 12.9338, "lon": 77.6061},
                    zoom=16.1,
                    height=540
                )
                fig_map.update_layout(
                    map_style="open-street-map",
                    margin=dict(l=0, r=0, t=10, b=0),
                    uirevision="campus_map"
                )
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.warning("No venue records match the current filter selection.")

    # -------------------------------------------------------------------
    # SUB-TAB 5: DATA EXPLORER & STATISTICAL SUMMARY
    # -------------------------------------------------------------------
    with tab5:
        with st.container(border=True):
            st.subheader("Searchable Campus Event Registry")
            search_q = st.text_input(
                "Search by Event ID, Event Name, Department, or Venue",
                placeholder="e.g., EVT-1001, Main Auditorium, Computer Science"
            )
            display_cols = [col for col in filtered_df.columns if col != "Date_dt"]
            explorer_df = filtered_df[display_cols].copy()

            if search_q:
                mask = (
                    explorer_df["Event_ID"].str.contains(search_q, case=False, na=False) |
                    explorer_df["Event_Name"].str.contains(search_q, case=False, na=False) |
                    explorer_df["Department"].str.contains(search_q, case=False, na=False) |
                    explorer_df["Venue"].str.contains(search_q, case=False, na=False)
                )
                explorer_df = explorer_df[mask]

            st.dataframe(
                explorer_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Utilization_Pct": st.column_config.ProgressColumn(
                        "Utilization", min_value=0, max_value=100, format="%.1f%%"
                    ),
                    "Est_Power_kWh": st.column_config.NumberColumn("Power (kWh)", format="%.1f")
                }
            )

            with st.expander("View NumPy & Pandas Descriptive Statistics"):
                num_cols = ["Venue_Capacity", "Duration_Hrs", "Expected_Footfall", "Actual_Footfall", "Utilization_Pct", "Est_Power_kWh"]
                st.dataframe(filtered_df[num_cols].describe().round(2), use_container_width=True)

# =======================================================================
# TOP TAB 2: REGISTRATION
# =======================================================================
with tab_registration:
    st.subheader("Register a New Campus Event")
    st.write("Submit event details below. NumPy overlap logic automatically checks for venue schedule clashes.")

    with st.form("event_registration_form"):
        f1, f2, f3 = st.columns(3)

        with f1:
            reg_name = st.text_input("Event Name", value="MCA Guest Lecture")
            reg_dept = st.selectbox("Department", [
                "Computer Science", "Management", "Commerce", "Psychology",
                "Law", "Physics", "Life Sciences", "Student Council", "Media Studies"
            ])
            reg_type = st.selectbox("Event Type", [
                "Guest Lecture", "Workshop", "Seminar", "Hackathon",
                "National Fest", "Cultural Audition", "Panel Discussion", "Conclave"
            ])

        with f2:
            reg_venue = st.selectbox("Select Venue", list(VENUE_INFO.keys()))
            reg_date = st.date_input("Event Date", value=pd.to_datetime("2026-11-25"))
            reg_av = st.selectbox("AV Setup Required", [
                "Full Sound + LED Wall", "Standard AV + Projector", "Basic Mic + Screen"
            ])

        with f3:
            reg_start = st.number_input("Start Hour (8 to 18)", min_value=8, max_value=18, value=10)
            reg_end = st.number_input("End Hour (9 to 19)", min_value=9, max_value=19, value=12)
            reg_footfall = st.number_input("Expected Footfall", min_value=10, max_value=800, value=150)

        submit_btn = st.form_submit_button("Register Event")

        if submit_btn:
            venue_cap = VENUE_INFO[reg_venue]["cap"]
            venue_block = VENUE_INFO[reg_venue]["block"]
            date_str = reg_date.strftime("%Y-%m-%d")

            if not reg_name.strip():
                st.error("Event Name cannot be empty.")
            elif reg_start >= reg_end:
                st.error("End Hour must be greater than Start Hour.")
            elif reg_footfall > venue_cap:
                st.error(f"Capacity Exceeded: {reg_venue} allows a maximum of {venue_cap} participants.")
            else:
                next_num = 1001 + len(st.session_state.events_df)
                new_id = f"EVT-{next_num}"

                # NumPy Schedule Clash Detection
                existing_df = st.session_state.events_df
                same_slot = existing_df[
                    (existing_df["Venue"] == reg_venue) &
                    (existing_df["Date"] == date_str) &
                    (existing_df["Booking_Status"] != "Cancelled")
                ]

                is_clash = False
                clash_msg = ""
                if not same_slot.empty:
                    starts = same_slot["Start_Hour"].to_numpy()
                    ends = same_slot["End_Hour"].to_numpy()
                    overlap = (reg_start < ends) & (reg_end > starts)
                    if np.any(overlap):
                        is_clash = True
                        clashing_event = same_slot[overlap].iloc[0]
                        clash_msg = (
                            f"Clashes with '{clashing_event['Event_Name']}' ({clashing_event['Event_ID']}) "
                            f"booked from {clashing_event['Start_Hour']}:00 to {clashing_event['End_Hour']}:00."
                        )

                status = "Clash Flagged" if is_clash else "Scheduled"
                est_power = np.round((reg_end - reg_start) * (venue_cap * 0.015), 1)

                new_record = pd.DataFrame([{
                    "Event_ID": new_id,
                    "Event_Name": reg_name.strip(),
                    "Department": reg_dept,
                    "Event_Type": reg_type,
                    "Venue": reg_venue,
                    "Block": venue_block,
                    "Venue_Capacity": venue_cap,
                    "Date": date_str,
                    "Start_Hour": int(reg_start),
                    "End_Hour": int(reg_end),
                    "Expected_Footfall": int(reg_footfall),
                    "Actual_Footfall": 0,
                    "AV_Setup": reg_av,
                    "Est_Power_kWh": float(est_power),
                    "Booking_Status": status
                }])

                st.session_state.events_df = pd.concat([st.session_state.events_df, new_record], ignore_index=True)

                if is_clash:
                    st.warning(f"Event {new_id} registered with status 'Clash Flagged'. {clash_msg}")
                else:
                    st.success(f"Event {new_id} ('{reg_name}') successfully scheduled in {reg_venue} on {date_str}!")

    st.divider()
    st.subheader("Venue Seating Capacity Reference")
    ref_df = pd.DataFrame([
        {"Venue": k, "Block": v["block"], "Max Capacity": v["cap"]}
        for k, v in VENUE_INFO.items()
    ])
    st.table(ref_df)